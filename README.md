# WG-Gesucht Bot 
*Let's face it, looking for a new WG is a pain, so why not just automate the process?*

Thanks to the code by [nickirk](https://github.com/nickirk/immo), which served as a starting point for this project.

## Getting Started

### 1 Create virtual environment and install Python packages

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### 2 Ensure `chromedriver` is installed

Running `which chromedriver` should return a path like `/usr/local/bin/chromedriver`.

If not simply run `sudo apt-get install chromedriver` if on Ubuntu.

Alternatively run `sudo apt-get install chromium-chromedriver` if on Raspberry OS.
`

### 3 Enter your email and password for WG-Gesucht into `login-creds.json`

```json
{
    "email": "my-email@gmail.com",
    "password": "password1234"
}
```

### 4 Write message into `message.txt`

### 5 Add your complete search URL into `wg-gesucht-spider.py`

Just go to the website, enter all your filter requirements, apply filter and simply copy the url you get.

Once you have copied the url, simply paste it into the `urls` list in `wg-gesucht-spider.py`.

### 6 Run **scrapy** to setup the bot structure

``` bash
scrapy startproject bot
```

After this you should have a new folder called `bot` with a strucuture like:

    bot/
        scrapy.cfg            # deploy configuration file
        bot/                  # project's Python module, you'll import your code from here
            __init__.py
            items.py          # project items definition file
            pipelines.py      # project pipelines file
            settings.py       # project settings file
            spiders/          # a directory where you'll later put your spiders
                __init__.py

### 7 Run bash script `create_symlinks.sh`

```terminal
bash create_symlinks.sh
```

After the folder structure should look like this:

    bot/
        wg-gesucht.py                   # symlink to file
        submit_wg.py                    # symlink to file
        login-creds.json                # symlink to file
        message.txt                     # symlink to file
        scrapy.cfg                      # deploy configuration file
        bot/                            # project's Python module, you'll import your code from here
            __init__.py
            items.py                    # project items definition file
            pipelines.py                # project pipelines file
            settings.py                 # project settings file
            spiders/                    # a directory where you'll later put your spiders
                __init__.py
                wg-gesucht-spider.py    # symlink to file


### 8 Finally, simply run

```
bash run.sh
```

The bash script will run the code headlessly, so that you can have it running 24/7 on a Raspberry Pi/in the cloud. If you would like to see the bot click through the webiste to get a better understanding of what is going on behind the scenes, you can add `--launch_type non-headless` to the last line of the bash script.

To have more fine grain control over how long the minimun rental period should be you can also use the `--min_rental_period` command line arg. See the bash script for how to use.

<!-- **testing** can be easily done by removing one of the id's from the `diff.dat` file. During the next check, the script will just consider this specific advertisement as a new one. -->
