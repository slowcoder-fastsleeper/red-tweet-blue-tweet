"""Write list of users who tweeted to a CSV, user_list.csv.

Assumptions:
 - MongoDB is listening on localhost/27017
 - The database is called "twitter" with collection "tweets_filtered"
"""

import csv

import pymongo


def export_userlist(client, collection_name):
    """Get all users in collection and export as CSV."""

    data = client["twitter"][collection_name].find()
    count = data.count()

    i = 0
    for tweet in data:
        # Track processed documents (enumerate didn't work for some reason)
        i += 1

        users = {}

        # Maintain users as hashmap of (user:number of tweets)
        try:
            users[tweet["user"]["id_str"]] += 1
        except:
            users[tweet["user"]["id_str"]] = 1

        if i % 50000 == 0:
            print("Processed {0}/{1} tweets".format(i, count))

    with open("user_list.csv", "w") as outfile:
        writer = csv.writer(csv_file)
        for user_id, num_tweets in users.items():
           writer.writerow([user_id, num_tweets])

    return


if __name__ == "__main__":
    client = pymongo.MongoClient("localhost", 27017)

    export_userlist(client, "tweets_filtered")