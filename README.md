# SWITCHtube-downloader
A Python cli-tool to download videos from SWITCHtube. Supports full organization / folder download and cookie caching. Great for automating video downloads to study from anywhere.

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/panmona/switchtube-dl/issues)


## Features
- Download videos from SWITCHtube.
- cli authentication with cookie caching.
- support for organization / channels and direct video download.
- now supports required OTP

## Future Features
- asynchronous downloads.
- interactive selection of channels / lectures in organization and channels.


## Disclaimer

**This software is intended strictly for **educational, legal, and personal use** only.**

The authors and contributors of this project **do not support, condone, or endorse any illegal use** of this software. By using this software, you agree to the following:

1. You are solely responsible for complying with all applicable copyright laws and terms of service for the content you download or interact with.
2. This software should **not be used** to download, distribute, or access **copyright-protected, restricted, or proprietary content** without explicit permission from the content owner or provider.
3. This project and its contributors are not liable for any misuse, and **no guarantees** are provided regarding functionality or legal compliance.

Please use this tool responsibly and ensure that any downloads comply with relevant terms of service and copyright laws.

---

**NOTE**: If you are uncertain about the legality of downloading specific content, please **consult the terms of service** for that content or seek legal advice.



## Installation

### Step 1: Set up a Virtual Environment

It is recommended to use a virtual environment to manage dependencies for this project. To set up a virtual environment, follow these steps:

1. **Create a virtual environment** by running the following command:
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. For more detailed guidance on virtual environments, refer to the [official Python documentation](https://docs.python.org/3/library/venv.html).

### Step 2: Install Requirements

With the virtual environment activated, install the required packages:
```bash
pip install -r requirements.txt
```

This will install all necessary dependencies listed in the `requirements.txt` file.



## Configuration (optional)

This project requires certain environment variables to be set up in a `.env` file to function correctly. Create a `.env` file in the root directory of the project and include the following information:

```plaintext
SCHOOL=your_school_name # This name should match the value in the dropdown when accessing `tube.switch.ch`
USERNAME=your_username
PASSWORD=your_password
```
Ensure that your `.env` file is securely stored and not shared publicly. You may want to add `.env` to your `.gitignore` file to prevent it from being committed to version control.


## Usage

This tool uses command-line arguments to specify the video or folder URL to download, as well as user credentials and configuration options. The following arguments are supported:

### Arguments:

- **`url`** (required): The URL of the video or folder you want to download.
- **`-u`, `--user`** (optional): The username required for authentication (if the service requires login).
- **`-p`, `--password`** (optional): The password for the specified username. If the `-u` (username) argument is provided, the `-p` (password) argument is required.
- **`-s`, `--school`** (optional): The university or school name for matching. This is required if the `-u` (username) is provided.
- **`-d`, `--dir`** (optional, default: `downloads`): The directory where the videos will be downloaded. If not provided, the default directory is `downloads`.
- **`--debug`** (optional): Run the browser in non-headless mode, showing the browser window (useful for debugging).

Once you run the program the CLI will ask you to provide your OTP code after which the download will proceed. Your token isn't stored but required to get the session cookie, which is then used for multiple downloads if you provided a link to a channel.

### Example Usage

To download a video or folder, run the following command with the required URL:

```bash
python main.py <url>
```

**Example 1**: Download a video with no user credentials (headless mode enabled by default):

```bash
python main.py https://example.com/video
```

**Example 2**: Download a video with user credentials provided via CLI:

```bash
python main.py https://example.com/video -u your_username -p your_password -s your_school
```

**Example 3**: Download a video with a specific directory and enabling the browser window:

```bash
python main.py https://example.com/video -d /path/to/downloads --debug
```

### Key Notes:
- values for `--user`, `--password` and `--school`can be set using the `.env` file as described above.
- **`--user` and `--password`**: If you provide a username using `--user`, you **must** also provide the corresponding password using `--password`.
- **`--school`**: This argument should be used along with `--user` to specify the associated university or school name for authentication.
- make sure to provide your OTP once prompted via CLI or the script will timeout.


