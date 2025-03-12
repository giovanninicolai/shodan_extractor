# shodan_extractor

This script, given a query for each port, each organization, and each city, allows you to extract IPs from the first and second pages of Shodan.

Configuration: enter the query found in the Shodan search URL (parameter query="") and the JSON containing the cookies of your Shodan account (I extract the cookies with j2teams cookies).

Usage example: python -u shodan_extractor.py | tee out.txt

The result may contain duplicates.

This script was created using an LLM, without any focus on optimization or similar concerns, take it as it is.

It is for demonstration and educational purposes only. I do not take responsibility for any illegal use.

