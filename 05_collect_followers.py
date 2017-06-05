"""Get followers for a group of political accounts."""


import csv
import itertools
import os
import pathlib

import time
import tweepy

from auth import authorize


def get_followers(auth):
    """Get lists of followers for various political accounts; write to files.

    This considers the union of the following groups:
     - member of congress (from CSPAN's list on Twitter)
     - governors (from CSPAN's list on Twitter)
     - other political accounts (from the paper and current events)
    
    Each gets written to a file "userid.csv".
    """

    # Authorize API
    api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

    congress = tweepy.Cursor(api.list_members, "cspan", "members-of-congress").items()
    governors = tweepy.Cursor(api.list_members, "cspan", "governors").items()
#     other_accts = ["BarackObama", "JoeBiden", "realDonaldTrump", "POTUS",
#                    "FLOTUS", "VP", "SecondLady", "WhiteHouse", "GOPLeader",
#                    "PressSec", "BetsyDeVos", "MichelleObama", "BernieSanders",
#                    "nytimes", "FoxNews", "NPR", "CNN", "NPR", "maddow",
#                    "rushlimbaugh", "glennbeck"]

    all_accounts = itertools.chain(congress, governors)

    # Get followers for each account; write to CSV
    for acct in all_accounts:
        # Keep those with at least 5000 followers
        if acct.followers_count < 5000:
            continue

        # For time purposes, ignore those with over 100k followers
        if acct.followers_count > 100000:
            print("Skipped {}".format(acct.id_str))
            continue

        user_id = acct.id_str

        # If we already made the followers list, skip it (because script may
        # be restarted occasionally)
        fname = "followers_lists/{}.csv".format(user_id)
        possible_file = pathlib.Path(fname)
        if possible_file.is_file():
            continue

        followers = []
        for page in tweepy.Cursor(api.followers_ids, id = user_id).pages():
            followers.extend(page)
            time.sleep(60)

        # Write list of followers to CSV
        fname = "followers_lists/{}.csv".format(user_id)
        with open(fname, "w") as outfile:
            writer = csv.writer(outfile)
            for follower in followers:
                writer.writerow([follower])

        print("Got followers for {0} / {1}".format(user_id, acct.name))


if __name__ == "__main__":
    # Create and authorize API
    auth = authorize()

    # Create output directory if it doesn't exist
    try:
        os.mkdir("followers_lists")
    except OSError:
        pass

    get_followers(auth)