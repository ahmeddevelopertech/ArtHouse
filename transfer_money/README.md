Overview
The Cash Transfer Between Branches module is a powerful solution developed by GeekXDigital that enables seamless cash
and bank transfers between different branches (companies) within your Odoo 17 environment. This module automates the
process of inter-branch transfers, creating accurate accounting entries in both the source and destination branches
while maintaining proper financial records.

This module is essential for businesses with multiple branches or companies that need to transfer funds between
locations while maintaining accurate financial records and audit trails.

💡 Key Features
✅ Multi-Company Cash Transfers: Transfer funds between different branches/companies
✅ Custom Cash Transfer Accounts: Define specific accounts for transfer transactions
✅ Real-time Journal Updates: Automatic creation of accounting entries in both branches
✅ Flexible Journal Selection: Choose from available cash/bank journals in each branch
✅ Permission Management: Control access with dedicated security groups
✅ User-Friendly Interface: Intuitive form with minimal required inputs
✅ Automated Clearing Accounts: Uses inter-company clearing accounts for accurate tracking
✅ Success Notifications: Clear feedback after successful transfers
✅ Multi-Currency Support: Handle transfers in different currencies
✅ Audit Trail: Complete history of all transfers with user and timestamp
📦 Requirements
Odoo Version: 17.0 (Enterprise Edition)
Required Apps: Accounting (account)
Supported Databases: PostgreSQL 12+
Server Requirements: Standard Odoo 17 server requirements
⚙️ Installation
Method 1: Using Odoo Apps Interface
Download the module ZIP file from your GeekXDigital portal
Log in to your Odoo database as an Administrator
Go to Apps → Update Apps List (top right)
Click Upload a custom module (top left)
Select the downloaded ZIP file and click Install
Method 2: Manual Installation (Recommended for Production)
bash

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17

# Navigate to your custom addons directory

cd /path/to/your/odoo/addons

# Extract the module (if downloaded as ZIP)

unzip custom_cash_transfer.zip

# Set proper permissions

chmod -R 755 custom_cash_transfer

# Restart Odoo service

sudo service odoo restart

# Update module list in Odoo

# Go to Apps → Update Apps List

# Install the module

# Search for "Cash Transfer Between Branches" and click Install

🔧 Configuration
Step 1: Configure Inter-Company Clearing Accounts
Go to Accounting → Configuration → Settings
Scroll down to Inter-Company Settings
For each company (branch):
Set Inter-Company Clearing Account
Ensure it's a liability account (typically under "2 - Liabilities")
Click Save
Step 2: Set Up Cash Transfer Accounts in Journals
Go to Accounting → Journals
Open each cash/bank journal you want to use for transfers
In the journal form:
Set Cash Transfer Account (typically a cash or current asset account)
This account will be used specifically for inter-branch transfers
If not set, the journal's default account will be used
Click Save
Step 3: Configure User Access Rights
Go to Settings → Users & Companies → Users
Select the user(s) who should have access to transfer cash between branches
Under Access Rights tab:
Add the user to Accounting → Cash Transfer Manager group
Click Save
🚀 Usage
Transferring Cash Between Branches
Go to Accounting → Cash Transfer (in the Finance menu)
Fill in the transfer details:
From Branch: Select the source branch (your current company by default)
To Branch: Select the destination branch
Source Cash Journal: Select the cash/bank journal in the source branch
Destination Cash Journal: Select the cash/bank journal in the destination branch
Amount: Enter the transfer amount
Date: Set the transfer date (today by default)
Click Transfer
Upon success:
You'll see a confirmation message
The window will automatically close
Accounting entries will be created in both branches
Important Notes
Only users in the Cash Transfer Manager group can transfer between branches
Regular users can only transfer within their registered branch
The system validates that all required accounts are properly configured
Transfers create two accounting entries (one in each branch) for accurate tracking
⚙️ Technical Details
How It Works
Source Branch Entry:
python

1
2
Debit: Inter-Company Clearing Account (Source Branch)
Credit: Cash Transfer Account (Source Journal)
Destination Branch Entry:
python

1
2
Debit: Cash Transfer Account (Destination Journal)
Credit: Inter-Company Clearing Account (Destination Branch)
Data Model
Model: cash.transfer
Fields:
source_company_id: Source branch (res.company)
dest_company_id: Destination branch (res.company)
source_journal_id: Source cash journal (account.journal)
dest_journal_id: Destination cash journal (account.journal)
amount: Transfer amount (float)
transfer_date: Date of transfer (date)
available_source_journal_ids: Helper field for UI (computed)
available_dest_journal_ids: Helper field for UI (computed)
Security Model
Security Group: group_cash_transfer_manager
Access Rules:
Regular users: Can only transfer within their registered branch
Cash Transfer Managers: Can transfer between any branches
Automatic validation ensures proper permissions
Integration Points
Accounting Module: Creates accounting entries in both branches
Multi-Company Framework: Uses Odoo's built-in multi-company features
Journal Configuration: Integrates with journal settings
📜 License
This module is licensed under the GNU Lesser General Public License v3 (LGPL-3).

1
2
3
4
5
6
7
8
9
10
11
12
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
📞 Support & Customization
For support, customization, or additional features, contact GeekXDigital:

Website: https://geekxdigital.com
Email: support@geekxdigital.com
Phone: +1 (555) 123-4567
Odoo Apps: GeekXDigital on Odoo Apps
Enterprise Support Package
GeekXDigital offers premium support packages including:

24/7 Technical Support
Customization Services
Performance Optimization
Security Audits
Training Sessions
Priority Bug Fixes
Contact us for details on our enterprise support packages!

Developed with ❤️ by GeekXDigital - Your Trusted Odoo Partner
© 2023 GeekXDigital. All rights reserved.