"""
Splitwise Phone Bill Module
Creates a new Splitwise expense titled "Phone Bill Due <date>"
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from module_base import ModuleBase
from splitwise import Splitwise
from splitwise.expense import Expense
from splitwise.user import ExpenseUser


class SplitwisePhoneBillModule(ModuleBase):
    """Module to create a Phone Bill expense in Splitwise"""

    # === Configuration ===
    # Replace with your actual credentials
    CONSUMER_KEY = "e71sl2WZXFbU08ampTM7YDpUVRJUgi3MSln7fAN0"
    CONSUMER_SECRET = "AgIRY5X26wEOL77bX6kYkGMqinzEYCxQPnzqm6VB"
    API_KEY = "Vpclwo6euyy8o6gtxBFeIdKDrAkLruMvbSEwc0Xy"
    GROUP_ID = 31014911  # Phone Bill
    TOTAL_COST = 560.0

    # Friend IDs and owed amounts
    USERS_OWED = {
        83976680: 40,  # Kas Johnson
        22444750: 50,  # Skye Nova
        48415524: 165,  # Fen Jensen
        23353628: 75,  # Ethan None
        22664155: 75,  # Hiro (Chris)
        51393333: 70,  # Elle Scott
    }

    @property
    def name(self) -> str:
        return "Splitwise: Phone Bill"

    @property
    def description(self) -> str:
        return "Create a new Splitwise expense for the monthly phone bill."

    @property
    def icon(self) -> str:
        return "📱"

    @property
    def color(self) -> str:
        return "#22c55e"  # green

    def get_status(self):
        """Return current module info and frontend elements."""
        return {
            "status": "Ready",
            "fields": [
                {
                    "id": "date_due",
                    "label": "Date Due",
                    "type": "text",
                    "placeholder": "YYYY-MM-DD",
                    "value": ""
                }
            ],
            "actions": [
                {
                    "id": "create_expense",
                    "label": "Create Splitwise Expense",
                    "variant": "primary"
                }
            ]
        }

    def get_actions(self):
        """Return backend actions supported by this module."""
        return [
            {
                "id": "create_expense",
                "label": "Create Splitwise Expense",
                "variant": "primary"
            }
        ]

    def execute_action(self, action_id: str, params=None):
        """Handle frontend action calls."""
        if action_id != "create_expense":
            return {"success": False, "error": f"Unknown action: {action_id}"}

        date_due = (params or {}).get("date_due", "").strip()
        if not date_due:
            return {"success": False, "error": "Please enter a Date Due value."}

        try:
            sObj = Splitwise(self.CONSUMER_KEY, self.CONSUMER_SECRET, api_key=self.API_KEY)
            current_user = sObj.getCurrentUser()
            gray_id = current_user.getId()

            # Build expense
            expense = Expense()
            expense.setGroupId(self.GROUP_ID)
            expense.setDescription(f"Phone Bill Due {date_due}")
            expense.setCost(str(self.TOTAL_COST))

            # Users list
            users = []
            remainder = self.TOTAL_COST - sum(self.USERS_OWED.values())

            gray_user = ExpenseUser()
            gray_user.setId(gray_id)
            gray_user.setPaidShare(str(self.TOTAL_COST))
            gray_user.setOwedShare(str(remainder))
            users.append(gray_user)

            for uid, owed in self.USERS_OWED.items():
                u = ExpenseUser()
                u.setId(uid)
                u.setPaidShare("0.00")
                u.setOwedShare(str(owed))
                users.append(u)

            expense.setUsers(users)

            expense, errors = sObj.createExpense(expense)
            if errors:
                return {"success": False, "error": str(errors.getErrors())}

            return {
                "success": True,
                "message": f"Expense created: '{expense.getDescription()}' (ID: {expense.getId()})"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}