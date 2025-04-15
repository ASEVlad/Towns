# Towns Selenium Script

## Description
A Selenium-based automation script for farming points / warming up Towns protocol. 
This script works directly with Dolphin or AdsPower anti-detection browsers.

## Important Note
This script must be executed on the local machine where Dolphin or AdsPower is installed AND running. 
It automatically opens browser profiles and interacts with the Towns protocol UI to farm points.


## Configuration

### 1. Copy the repository from GitHub
```bash
git clone https://github.com/ASEVlad/Towns.git
cd Towns/
```

### 2. Set up local files
1. Create `.env` in the Towns folder and fill it similarly to `env.example`
   - OPEN_AI_API is required.
     - Go to https://platform.openai.com/settings/organization/api-keys
     - Click "Create new secret key" and copy the key
     - Go to https://platform.openai.com/account/billing
     - Under "Payment methods", add a credit/debit card. 
     - Click "Add to balance" to top up your account
   - everything else is optional. But keep in mind, if:
     - ADS_API_URL usually standard so you can not specify it. But if you have some errors with it - check it out.
     - if you want to run few accounts in parallel - adjust PARALLEL_ACCOUNTS (if equals to 1 - then not parallel)
     - you want to use OKX withdrawal - adjust OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSWORD
     - you want to use BINANCE withdrawal - adjust BINANCE_API_KEY, BINANCE_API_SECRET

2. Create `profile.csv` and fill it similarly to `profiles.example.csv`
   - Basically it is a table with 3 columns
     - profile_id
     - anty_type : is type of your anty browser. Current options: "dolphin" or "adspower"
     - login_with : is the the name os the social media with what you want to be authorized. Current options: "twitter" or "google"

3. Create `actions.txt` and fill it with your desired actions (see Available Actions section further)

4. Add town links to `Towns/data/state_towns.txt` with 1 or more links of Towns you want to use for farming points
   - For the cheapest option of farming points manually create Town in your main account with state price. 90% of the price will be brought back to your account.
   - Just provide links for those towns similarly to data/free_towns.txt or data/dynamic_towns.txt

5. Adjust geckodriver:
   - Direct link: https://anty-browser.s3.eu-central-1.amazonaws.com/chromedriver-134.zip
   - Or manually download from https://help.dolphin-anty.com/en/articles/7127390-basic-automation-dolphin-anty using the "Download ChromeDriver" button
   - After downloading unzip the files and put the chromedriver for your system to the data folder in main folder of the script (TOWNS) 
   - This step could cause the error. So be sure that you have downloaded the same version of the browser as you are using in kernel in you profiles in anty browser. The latest version is 134


### 3. Open your anti-detection browser
- This can be either Dolphin or AdsPower

### 4. Run the script
```bash
# Create and activate virtual environment
python -m venv venv

# Activate the environment (choose appropriate command for your OS)
source venv/bin/activate  # for macOS/Linux
venv\Scripts\activate     # for Windows

# Run the script
python main.py
```

**If you don't want to create your own list of actions**, you can simply use one of the actions below (just choose between binance or okx).
I would recommend binance option since it is much easier AND you can start earn points straightaway from the first run
Just ensure you have followed the steps mentioned above.

### If you use BINANCE to withdraw your funds:

Set up API for binance:
- Go to https://www.binance.com/en/my/settings/api-management
- Create API
- Copy paste API_KEY and SECRET_KEY to your .env file
- Change restriction to IP restriction
- Go to https://www.myip.com/
- Copy paste your ip
- Click "Enable Withdraw"

#### FIRST RUN:
```bash
binance_withdraw -bottom_limit_range=0.0155 -top_limit_range=0.0185
create_free_channel -chance=70%
create_dynamic_channel -chance=50%
create_state_channel -chance=20% -cost=0.1
join_free_channel -chance=70%
join_dynamic_channel -chance=50% -cost_limit=0.001
join_state_channel -chance=30% -cost_limit=0.1
get_daily_points -chance=95%
write_message -chance=70% -town_type=state -number=3 -cooldown=10
write_message -chance=70% -town_type=dynamic -number=2 -cooldown=10
write_message -chance=70% -town_type=free -number=1 -cooldown=10
```


#### SECOND RUN:
Just the same as previous, but WITHOUT withdrawing.

```bash
create_free_channel -chance=70%
create_dynamic_channel -chance=50%
create_state_channel -chance=20% -cost=0.1
join_free_channel -chance=70%
join_dynamic_channel -chance=50% -cost_limit=0.001
join_state_channel -chance=30% -cost_limit=0.1
get_daily_points -chance=95%
write_message -chance=70% -town_type=state -number=3 -cooldown=10
write_message -chance=70% -town_type=dynamic -number=2 -cooldown=10
write_message -chance=70% -town_type=free -number=1 -cooldown=10
```

### If you use OKX to withdraw your funds:
#### FIRST RUN:
```bash
create_free_channel -chance=70%
create_dynamic_channel -chance=50%
create_state_channel -chance=20% -cost=0.1
join_free_channel -chance=70%
write_message -chance=100% -town_type=free -number=2 -cooldown=10
```

#### Set Up OKX API
- Go to https://www.okx.com/ua/account/my-api
- Generate your API
- Copy paste your API, SECRET, PASSPHRASE(password) for the API.

And now you should add all the wallets to your whitelist.
- Go to https://www.okx.com/ua/balance/withdrawal-address
- Click "Add address" → "Add few addresses"
- Paste your addresses from `data/towns_wallets.txt` (choose EVM or ETH, Base)
- click confirm all addresses
- Click "Save addresses"
- Done

#### SECOND RUN:
```bash
okx_withdraw -bottom_limit_range=0.0125 -top_limit_range=0.0175 OR binance_withdraw -bottom_limit_range=0.0125 -top_limit_range=0.0175
create_free_channel -chance=70%
create_dynamic_channel -chance=50%
create_state_channel -chance=20% -cost=0.1
join_free_channel -chance=70%
join_dynamic_channel -chance=50% -cost_limit=0.001
join_state_channel -chance=30% -cost_limit=0.1
get_daily_points -chance=95%
write_message -chance=70% -town_type=state -number=3 -cooldown=10
write_message -chance=70% -town_type=dynamic -number=2 -cooldown=10
write_message -chance=70% -town_type=free -number=1 -cooldown=10
```

I recommend depositing the cost of the Town you want to abuse for fast farming along with an additional deposit of 5-10 USD in ETH equivalent (approximately 0.0025-0.005 ETH at present).

### **Disclaimer:** 
All actions will be randomly executed during profile runtime, except:
- `okx_withdraw`, which is executed at the beginning.
- `binance_withdraw`, which is executed at the beginning.
- `write_message`, which is executed at the end.



## Available Actions

The script supports the following actions:

### 1. `create_free_channel`
Creates a Free Channel with generated logo and name. The channel link is saved to `data/towns_links/free_towns`.

**Arguments:**
- `-chance`: Probability of execution (e.g., 90% means approximately 9 out of 10 accounts will execute this action)

**Examples:**
```
create_free_channel -chance=90%
```

**Default:** `create_free_channel -chance=100%`

### 2. `create_dynamic_channel`
Creates a Channel with DYNAMIC pricing, including generated logo and name. The channel link is saved to `data/towns_links/dynamic_towns`.

**Arguments:**
- `-chance`: Probability of execution

**Examples:**
```
create_dynamic_channel -chance=50%
```

**Default:** `create_dynamic_channel -chance=100%`

### 3. `create_state_channel`
Creates a Channel with STATIC pricing, including generated logo and name. The channel link is saved to `data/towns_links/state_towns`.

**Arguments:**
- `-chance`: Probability of execution
- `-cost`: Price for joining the created town (in ETH)

**Examples:**
```
create_state_channel -chance=6% -cost=0.2
```

**Default:** `create_state_channel -chance=100% -cost=0.1`

### 4. `join_free_channel`
Joins a FREE channel from the list in `/data/towns_links/free_towns`. This file contains towns created by the script using the `create_free_channel` function across all profiles.

**Arguments:**
- `-chance`: Probability of execution

**Examples:**
```
join_free_channel -chance=20%
```

**Default:** `join_free_channel -chance=100%`

### 5. `join_dynamic_channel`
Joins a channel with DYNAMIC pricing from the list in `/data/towns_links/dynamic_towns`.

**Arguments:**
- `-chance`: Probability of execution
- `-cost_limit`: Maximum price you're willing to pay in ETH

**Note:** For Dynamic channels, the price grows logarithmically:
- 10 participants → price = 1 + log(10) = 2 USD (~0.001 ETH)
- 20 participants → price = 1 + log(20) = 2.3 USD (~0.00115 ETH)

**Examples:**
```
join_dynamic_channel -chance=20% -cost_limit=0.01
```

**Default:** `join_dynamic_channel -chance=100% -cost_limit=0.001`

### 6. `join_state_channel`
Joins a channel with STATIC pricing from the list in `/data/towns_links/state_towns`. **This is the recommended option for farming points.**

**Arguments:**
- `-chance`: Probability of execution
- `-cost_limit`: Maximum price you're willing to pay in ETH
- `-link`: Specific town link (optional)

**Examples:**
```
join_state_channel -chance=20% -cost_limit=1.0 -link=https://app.towns.com/t/0xdc443716b9c203ff3ee9f3631182bfedf205dac8/
```

**Default:** `join_state_channel -chance=100% -cost_limit=0.1`

### 7. `write_message`
Writes AI-generated messages in channels.

**Arguments:**
- `-chance`: Probability of execution
- `-town_type`: Type of town to write messages in ("free", "dynamic", or "state")
- `-number`: Number of messages to write
- `-cooldown`: Delay between messages (in seconds)
- `-link`: Specific town link (optional)

**Examples:**
```
write_message -chance=80% -town_type=free -number=5 -cooldown=30 -link=https://app.towns.com/t/0xdc443716b9c203ff3ee9f3631182bfedf205dac8/
```

**Default:** `write_message -chance=100% -town_type=state -number=3 -cooldown=20`

### 8. `get_daily_points`
Claims daily points (rubs the beaver belly).

**Arguments:**
- `-chance`: Probability of execution

**Examples:**
```
get_daily_points -chance=100%
```

**Default:** `get_daily_points -chance=100%`

### 9. `okx_withdraw`
Withdraws funds from OKX to your Town wallet.

**Arguments:**
- `-bottom_limit_range`: Minimum withdrawal amount (in ETH)
- `-top_limit_range`: Maximum withdrawal amount (in ETH)

**Examples:**
```
okx_withdraw -bottom_limit_range=0.005 -top_limit_range=0.01"
```

**Default:** `binance_withdraw -bottom_limit_range=0.0125 -top_limit_range=0.0175`

### 10. `binance_withdraw`
Withdraws funds from OKX to your Town wallet.

**Arguments:**
- `-bottom_limit_range`: Minimum withdrawal amount (in ETH)
- `-top_limit_range`: Maximum withdrawal amount (in ETH)

**Examples:**
```
binance_withdraw -bottom_limit_range=0.005 -top_limit_range=0.01
```

**Default:** `binance_withdraw -bottom_limit_range=0.0125 -top_limit_range=0.0175`

### 11. `set_profile_avatar`
Withdraws funds from OKX to your Town wallet.

**Arguments:**
- `-chance`: Probability of execution

**Examples:**
```
set_profile_avatar -chance=0.9
```

**Default:** `set_profile_avatar -chance=1.0`

### 12. `write_review`
Withdraws funds from OKX to your Town wallet.

**Arguments:**
- `-chance`: Probability of execution
- `-town_type`: Type of town to write messages in ("free", "dynamic", "state" or "random")
- `-link`: Specific town link (optional)

**Examples:**
```
write_review -chance=0.9 -link=https://app.towns.com/t/0xdc443716b9c203ff3ee9f3631182bfedf205dac8/
```

**Default:** `write_review -chance=1.0 -town_type=random`
