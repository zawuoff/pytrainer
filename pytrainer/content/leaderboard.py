"""The eval leaderboard's fixed data: a small product-docs corpus and two question sets.

DEV questions are shown to the learner for tuning. TEST questions are held out: the leaderboard
ranks on them, so tuning that only fits the dev set shows up as a gap between the two scores.
`source` is the document that answers the question, or None when the docs don't say (the right
behaviour is then to refuse).
"""

CORPUS = {
    "docs/getting-started.md": """# Getting started with Orbit

Orbit is a note-taking app for teams. Install it from orbit.example/download; it runs on Windows, macOS and Linux.

Create your first notebook with Ctrl+N. Every notebook can hold up to 5,000 notes.

New accounts start on the Free plan, which includes 2 GB of storage.
""",
    "docs/pricing.md": """# Plans and pricing

The Free plan costs nothing and includes 2 GB of storage and 3 shared notebooks.

The Team plan costs 8 dollars per user per month, billed yearly, and includes 100 GB of storage per user.

Students get the Team plan at half price with a school email address.
""",
    "docs/sync.md": """# Sync

Orbit syncs your notes every 30 seconds while you are online.

Offline edits are kept on your device and uploaded the next time you connect.

If two people edit the same note offline, Orbit keeps both versions and marks the note as a conflict.
""",
    "docs/export.md": """# Export and backup

You can export a notebook as Markdown, PDF or HTML from File > Export.

Automatic backups run every night at 2 am and are kept for 30 days.

Deleted notes stay in the trash for 14 days before they are removed for good.
""",
    "docs/shortcuts.md": """# Keyboard shortcuts

Ctrl+K opens the command palette. Ctrl+Shift+F searches every notebook at once.

Ctrl+B makes text bold and Ctrl+I makes it italic.

Press Alt+Up or Alt+Down to move the current line.
""",
    "docs/security.md": """# Security and privacy

All notes are encrypted at rest with AES-256 and in transit with TLS 1.3.

Two-factor authentication can be turned on under Settings > Account > Security.

Orbit never uses your notes to train machine learning models.
""",
    "docs/ai-assistant.md": """# The AI assistant

The AI assistant can summarise a note, draft a reply or answer questions about a notebook.

It is available on the Team plan and allows 500 AI requests per user each month.

Answers from the assistant cite the notes they are based on.
""",
    "docs/troubleshooting.md": """# Troubleshooting

If sync stops, sign out and sign back in; this refreshes your session token.

A red cloud icon means Orbit cannot reach the server. Check your network or proxy settings.

Logs are saved in the Orbit folder under logs/orbit.log and help support find problems.
""",
    "docs/integrations.md": """# Integrations

Orbit connects to Slack: share a note into a channel with the /orbit command.

The calendar integration turns meeting invites into notes with the agenda filled in.

Developers can use the REST API with a personal access token from Settings > Developer.
""",
    "docs/admin.md": """# Team admin

Admins can invite members by email and remove them from the Members page.

Single sign-on with SAML is available for teams of 20 users or more.

The audit log keeps a record of every sign-in and permission change for 1 year.
""",
}

DEV = [
    {"q": "How much storage does the Free plan include?", "source": "docs/pricing.md"},
    {"q": "How often does Orbit sync notes when online?", "source": "docs/sync.md"},
    {"q": "Which formats can I export a notebook to?", "source": "docs/export.md"},
    {"q": "What shortcut opens the command palette?", "source": "docs/shortcuts.md"},
    {"q": "How are notes encrypted at rest?", "source": "docs/security.md"},
    {"q": "How many AI requests does each user get per month?", "source": "docs/ai-assistant.md"},
    {"q": "What does a red cloud icon mean?", "source": "docs/troubleshooting.md"},
    {"q": "How do I share a note into a Slack channel?", "source": "docs/integrations.md"},
    {"q": "Does Orbit have a dark mode for the mobile app?", "source": None},
    {"q": "Can I pay for Orbit with cryptocurrency?", "source": None},
]

TEST = [
    {"q": "How long do deleted notes stay in the trash?", "source": "docs/export.md"},
    {"q": "What happens when two people edit the same note offline?", "source": "docs/sync.md"},
    {"q": "How much does the Team plan cost per user?", "source": "docs/pricing.md"},
    {"q": "Where can I turn on two-factor authentication?", "source": "docs/security.md"},
    {"q": "How many notes can one notebook hold?", "source": "docs/getting-started.md"},
    {"q": "Which shortcut searches every notebook at once?", "source": "docs/shortcuts.md"},
    {"q": "How big must a team be to use single sign-on?", "source": "docs/admin.md"},
    {"q": "Where are the Orbit log files saved?", "source": "docs/troubleshooting.md"},
    {"q": "Can Orbit translate my notes into Japanese?", "source": None},
    {"q": "Is there a lifetime licence I can buy once?", "source": None},
]
