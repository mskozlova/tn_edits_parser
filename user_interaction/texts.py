START = (
    "👋 This bot can track your latest Tech Nation application and notify you of new edits.\n\n"
    "You can track multiple accounts. Add tracking: /track\n\n"
    "Please make sure to stop tracking the account after you receive an answer: /stop"
)

EMAIL = (
    "I'll need your TN account credentials to parse application status. I promise to use them responsibly and not to peek.\n\n"
    "📩 Enter email of the account you want to track:"
)

PASSWORD = "🗝 Enter password:"

EMAIL_TO_DELETE = "📩 Enter email you want to stop tracking.\n\nTracked emails:\n{}"

EMAIL_NOT_FOUND = "Email not found. Please choose one of your tracked emails:\n{}"

EMAIL_DELETED = "Tracking stopped!"

CANCEL = "Cancelled!"

TRACKING_STARTED = "✅ You now track edits for account {}.\nI'll notify you when the latest application is edited from now on.\nGood luck!"

TRACKING_FAILED = (
    "❌ Login failed.\nPlease check credentials and try one more time: /track"
)
