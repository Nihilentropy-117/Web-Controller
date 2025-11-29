"""
Receipt Splitter Module
Uploads receipt images, parses them with AI, and creates split Splitwise expenses
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from module_base import ModuleBase
from splitwise import Splitwise
from splitwise.expense import Expense
from splitwise.user import ExpenseUser
import tomli
import base64
import json
import requests
from typing import Dict, Any, List
import secrets


class ReceiptSplitterModule(ModuleBase):
    """Module to split receipts among Splitwise group members"""

    # Class-level storage for processing sessions
    sessions: Dict[str, Dict[str, Any]] = {}

    def __init__(self):
        # Load configuration from config.toml
        config_path = Path(__file__).parent.parent / 'config.toml'
        with open(config_path, 'rb') as f:
            config = tomli.load(f)

        splitwise_config = config.get('splitwise', {})
        openrouter_config = config.get('openrouter', {})

        # Splitwise credentials
        self.CONSUMER_KEY = splitwise_config.get('consumer_key')
        self.CONSUMER_SECRET = splitwise_config.get('consumer_secret')
        self.API_KEY = splitwise_config.get('api_key')

        # OpenRouter credentials
        self.OPENROUTER_API_KEY = openrouter_config.get('api_key')

    @property
    def name(self) -> str:
        return "Receipt Splitter"

    @property
    def description(self) -> str:
        return "Upload receipt images, AI parses items, and split costs among group members."

    @property
    def icon(self) -> str:
        return "🧾"

    @property
    def color(self) -> str:
        return "#8b5cf6"  # purple

    def get_status(self):
        """Return current module info and frontend elements."""
        return {
            "status": "Ready to upload",
            "info": "Upload 1-10 receipt images from your mobile device",
            "fields": [
                {
                    "id": "group_id",
                    "label": "Splitwise Group",
                    "type": "select",
                    "placeholder": "Select a group",
                    "options": [],  # Will be populated by frontend API call
                    "value": ""
                },
                {
                    "id": "receipt_images",
                    "label": "Receipt Images (1-10)",
                    "type": "file",
                    "accept": "image/*",
                    "multiple": True,
                    "capture": "environment",  # Suggests camera on mobile
                    "value": ""
                }
            ]
        }

    def get_actions(self):
        """Return backend actions supported by this module."""
        return [
            {
                "id": "fetch_groups",
                "label": "🔄 Load Groups",
                "variant": "secondary"
            },
            {
                "id": "process_receipt",
                "label": "🚀 Process Receipt",
                "variant": "primary"
            }
        ]

    def execute_action(self, action_id: str, params=None):
        """Handle frontend action calls."""
        if action_id == "fetch_groups":
            return self._fetch_groups()
        elif action_id == "process_receipt":
            return self._process_receipt(params or {})
        elif action_id == "fetch_group_users":
            return self._fetch_group_users(params or {})
        elif action_id == "create_split_expense":
            return self._create_split_expense(params or {})
        else:
            return {"success": False, "error": f"Unknown action: {action_id}"}

    def _fetch_groups(self):
        """Fetch all Splitwise groups for the user."""
        try:
            sObj = Splitwise(self.CONSUMER_KEY, self.CONSUMER_SECRET, api_key=self.API_KEY)
            groups = sObj.getGroups()

            group_list = []
            for group in groups:
                group_list.append({
                    "id": group.getId(),
                    "name": group.getName()
                })

            return {
                "success": True,
                "groups": group_list,
                "message": f"Found {len(group_list)} groups"
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to fetch groups: {str(e)}"}

    def _process_receipt(self, params: Dict[str, Any]):
        """Process uploaded receipt images with OpenRouter AI."""
        group_id = params.get("group_id", "").strip()
        images_data = params.get("images", [])

        if not group_id:
            return {"success": False, "error": "Please select a Splitwise group"}

        if not images_data or len(images_data) == 0:
            return {"success": False, "error": "Please upload at least one receipt image"}

        if len(images_data) > 10:
            return {"success": False, "error": "Maximum 10 images allowed"}

        try:
            # Parse receipt items using OpenRouter
            items = self._parse_receipt_with_ai(images_data)

            if not items:
                return {"success": False, "error": "No items found on receipt"}

            # Create a session token for this processing
            session_token = secrets.token_urlsafe(32)

            # Store session data
            self.sessions[session_token] = {
                "group_id": group_id,
                "items": items,
                "images": images_data
            }

            return {
                "success": True,
                "message": f"Found {len(items)} items on receipt",
                "session_token": session_token,
                "items": items,
                "group_id": group_id
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to process receipt: {str(e)}"}

    def _parse_receipt_with_ai(self, images_data: List[str]) -> Dict[str, float]:
        """Send images to OpenRouter for parsing with structured outputs."""

        # Prepare image messages for the API
        image_content = []
        for img_data in images_data:
            # img_data should be base64 encoded
            image_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_data}"
                }
            })

        # Add text prompt
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Analyze these receipt or purchase order images and extract ALL items with their costs.
Return a JSON object where each key is the item name and the value is the price as a number.
Combine all items from all images into one object.
If multiple images show the same receipt, don't duplicate items.
Example format: {"Milk": 4.99, "Bread": 3.50, "Eggs": 5.99}"""
                    }
                ] + image_content
            }
        ]

        # Call OpenRouter API with structured outputs
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.0-flash-001:free",  # Free vision model
                "messages": messages,
                "response_format": {
                    "type": "json_object"
                }
            }
        )

        if response.status_code != 200:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

        result = response.json()

        # Extract the items from the response
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        items_dict = json.loads(content)

        # Ensure all values are floats
        parsed_items = {}
        for item_name, price in items_dict.items():
            try:
                parsed_items[item_name] = float(price)
            except (ValueError, TypeError):
                # Skip items with invalid prices
                continue

        return parsed_items

    def _fetch_group_users(self, params: Dict[str, Any]):
        """Fetch all users in the selected group."""
        group_id = params.get("group_id", "").strip()

        if not group_id:
            return {"success": False, "error": "Group ID is required"}

        try:
            sObj = Splitwise(self.CONSUMER_KEY, self.CONSUMER_SECRET, api_key=self.API_KEY)
            group = sObj.getGroup(id=int(group_id))

            users_list = []
            for member in group.getMembers():
                users_list.append({
                    "id": member.getId(),
                    "first_name": member.getFirstName(),
                    "last_name": member.getLastName() or "",
                    "name": f"{member.getFirstName()} {member.getLastName() or ''}".strip()
                })

            return {
                "success": True,
                "users": users_list,
                "message": f"Found {len(users_list)} users in group"
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to fetch group users: {str(e)}"}

    def _create_split_expense(self, params: Dict[str, Any]):
        """Create a Splitwise expense with the calculated splits."""
        session_token = params.get("session_token", "").strip()
        item_splits = params.get("item_splits", {})  # {item_name: [user_ids]}
        expense_description = params.get("description", "Receipt Split")

        if not session_token or session_token not in self.sessions:
            return {"success": False, "error": "Invalid or expired session"}

        session_data = self.sessions[session_token]
        group_id = session_data["group_id"]
        items = session_data["items"]

        if not item_splits:
            return {"success": False, "error": "No item splits provided"}

        try:
            sObj = Splitwise(self.CONSUMER_KEY, self.CONSUMER_SECRET, api_key=self.API_KEY)
            current_user = sObj.getCurrentUser()
            current_user_id = current_user.getId()

            # Calculate how much each person owes
            user_totals = {}  # {user_id: total_amount}

            for item_name, participant_ids in item_splits.items():
                if item_name not in items:
                    continue

                item_price = items[item_name]
                num_participants = len(participant_ids)

                if num_participants == 0:
                    continue

                # Split the item cost equally among participants
                split_amount = item_price / num_participants

                for user_id in participant_ids:
                    user_id_int = int(user_id)
                    user_totals[user_id_int] = user_totals.get(user_id_int, 0.0) + split_amount

            # Calculate total cost
            total_cost = sum(items.values())

            # Create the expense
            expense = Expense()
            expense.setGroupId(int(group_id))
            expense.setDescription(expense_description)
            expense.setCost(f"{total_cost:.2f}")

            # Build users list
            users = []

            # Current user pays the full amount
            payer = ExpenseUser()
            payer.setId(current_user_id)
            payer.setPaidShare(f"{total_cost:.2f}")
            payer.setOwedShare(f"{user_totals.get(current_user_id, 0.0):.2f}")
            users.append(payer)

            # Add all other users
            for user_id, owed_amount in user_totals.items():
                if user_id == current_user_id:
                    continue  # Already added as payer

                user = ExpenseUser()
                user.setId(user_id)
                user.setPaidShare("0.00")
                user.setOwedShare(f"{owed_amount:.2f}")
                users.append(user)

            expense.setUsers(users)

            # Create the expense on Splitwise
            expense, errors = sObj.createExpense(expense)
            if errors:
                return {"success": False, "error": str(errors.getErrors())}

            # Clean up session
            del self.sessions[session_token]

            return {
                "success": True,
                "message": f"Expense created: '{expense.getDescription()}' (ID: {expense.getId()})",
                "expense_id": expense.getId()
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to create expense: {str(e)}"}
