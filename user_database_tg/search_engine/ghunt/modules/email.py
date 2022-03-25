import asyncio
import collections
from datetime import datetime
from datetime import datetime
from io import BytesIO
from pathlib import Path

import aiofiles
import httpx
from PIL import Image
from geopy.geocoders import Nominatim
from loguru import logger

from user_database_tg.search_engine.ghunt import config
from user_database_tg.search_engine.ghunt.lib import calendar as gcalendar
from user_database_tg.search_engine.ghunt.lib import gmaps
from user_database_tg.search_engine.ghunt.lib import youtube as ytb
from user_database_tg.search_engine.ghunt.lib.utils import (
    detect_default_profile_pic,
    get_account_data,
    image_hash,
    is_email_google_account,
    update_emails,
    CookieExpiredError,
    NotGoogleAccountError,
)


async def get_profile_pic(client, account, account_info, email):
    profile_pic_url = account.get("profile_pics") and account["profile_pics"][0].url
    if profile_pic_url:
        req = await client.get(profile_pic_url)

        # TODO: make sure it's necessary now
        profile_pic_img = Image.open(BytesIO(req.content))
        profile_pic_flathash = image_hash(profile_pic_img)
        is_default_profile_pic = detect_default_profile_pic(profile_pic_flathash)

        if not is_default_profile_pic:
            logger.trace("\n[+] Custom profile picture !")
            logger.trace(f"=> {profile_pic_url}")
            account_info["Profile picture"] = profile_pic_url

            if config.write_profile_pic:
                profile_photo_path = Path(config.profile_pics_dir) / f"{email}.jpg"
                async with aiofiles.open(profile_photo_path, "wb") as f:
                    await f.write(req.content)
                # with open(Path(config.profile_pics_dir) / f"{email}.jpg", "wb") as f:
                #     f.write(req.content)
                logger.trace("Profile picture saved !")
        else:
            # account_info["profile picture"] = None
            logger.trace("\n[-] Default profile picture")

    return profile_pic_flathash


async def get_cover_profile_pic(client, account, account_info, email):
    cover_pic = account.get("cover_pics") and account["cover_pics"][0]
    if cover_pic and not cover_pic.is_default:
        cover_pic_url = cover_pic.url
        req = await client.get(cover_pic_url)

        logger.trace("\n[+] Custom profile cover picture !")
        logger.trace(f"=> {cover_pic_url}")
        account_info["Cover profile picture"] = cover_pic_url
        if config.write_profile_pic:
            profile_photo_path = Path(config.profile_pics_dir) / f"cover_{email}.jpg"
            async with aiofiles.open(profile_photo_path, "wb") as f:
                await f.write(req.content)
            # open(Path(config.profile_pics_dir) / f"cover_{email}.jpg", "wb").write(req.content)
            logger.trace("Cover profile picture saved !")
    # else:
    #     account_info["cover profile picture"] = None


async def get_last_edit(account_info, infos):
    try:
        timestamp = int(infos["metadata"]["lastUpdateTimeMicros"][:-3])
        last_edit = datetime.utcfromtimestamp(timestamp).strftime("%Y/%m/%d %H:%M:%S (UTC)")
        account_info["Last profile edit"] = last_edit
        logger.trace(f"\nLast profile edit : {last_edit}")
    except KeyError:
        last_edit = None
        # account_info["last profile edit"] = last_edit
        logger.trace(f"\nLast profile edit : Not found")


async def get_calendar(client, account_info, email):
    calendar_response = await gcalendar.fetch(email, client, config, account_info)
    if calendar_response:
        logger.trace("[+] Public Google Calendar found !")
        events = calendar_response["events"]
        if events:
            gcalendar.out(events, account_info)
        else:
            logger.trace("=> No recent events found.")
    else:
        logger.trace("[-] No public Google Calendar.")


async def get_email(account, account_info, infos, email, gaiaID):
    canonical_email = ""
    emails = update_emails(account["emails_set"], infos)
    if emails and len(list(emails)) == 1:
        if list(emails.values())[0].is_normalized(email):
            new_email = list(emails.keys())[0]
            if email != new_email:
                canonical_email = f" (canonical email is {new_email})"
            emails = []

    logger.trace(f"\nEmail : {email}{canonical_email}\nGaia ID : {gaiaID}\n")
    account_info["Email"] = f"{email}{canonical_email}"
    account_info["Gaia ID"] = gaiaID

    if emails:
        contact_emails = {", ".join(map(str, emails.values()))}
        account_info["Contact emails"] = contact_emails
        logger.trace(f"Contact emails : {contact_emails}")

    phones = account["phones"]
    if phones:
        account_info["Contact phones"] = phones
        logger.trace(f"Contact phones : {phones}")


async def is_bot(account_info, infos):
    if "extendedData" in infos:
        isBot = infos["extendedData"]["hangoutsExtendedData"]["isBot"]
        if isBot:
            account_info["Hangouts Bot"] = "Yes"
            logger.trace("Hangouts Bot : Yes !")
        else:
            logger.trace("Hangouts Bot : No")
    else:
        logger.trace("Hangouts Bot : Unknown")


async def get_youtube(client, name, account_info, infos, profile_pic_flathash):
    # decide to check YouTube
    ytb_hunt = False
    try:
        services = [
            x["appType"].lower() if x["appType"].lower() != "babel" else "hangouts" for x in infos["inAppReachability"]
        ]
        if name and (config.ytb_hunt_always or "youtube" in services):
            ytb_hunt = True
        activated_google_services = "\n".join(["- " + x.capitalize() for x in services])
        logger.trace("\n[+] Activated Google services :")
        account_info["Activated Google services"] = activated_google_services
        logger.trace(activated_google_services)

    except KeyError:
        ytb_hunt = True
        logger.trace("\n[-] Unable to fetch connected Google services.")

    # check YouTube
    if name and ytb_hunt:
        confidence = None
        data = await ytb.get_channels(client, name, config.data_path, config.gdocs_public_doc)
        if not data:
            logger.trace("\n[-] YouTube channel not found.")
        else:
            confidence, channels = ytb.get_confidence(data, name, profile_pic_flathash)

            if confidence:
                logger.trace(f"\n[+] YouTube channel (confidence => {confidence}%) :")
                account_info[f"YouTube channel (confidence => {confidence}%)"] = "\n" + "\n".join(
                    f"- [{channel['name']}]\n=>{channel['profile_url']}" for channel in channels
                )

                for channel in channels:
                    logger.trace(f"- [{channel['name']}] {channel['profile_url']}")
                possible_usernames = ytb.extract_usernames(channels)
                if possible_usernames:
                    account_info["Possible usernames found"] = "\n".join(
                        f"- {username}" for username in possible_usernames
                    )
                    logger.trace("\n[+] Possible usernames found :")
                    for username in possible_usernames:
                        logger.trace(f"- {username}")
            else:
                logger.trace("\n[-] YouTube channel not found.")


async def get_reviews(client, account_info, gaiaID, cookies, geolocator):
    reviews = await gmaps.scrape(
        gaiaID,
        client,
        cookies,
        config,
        config.headers,
        config.regexs["review_loc_by_id"],
        config.headless,
        account_info,
    )

    if reviews:
        confidence, locations = gmaps.get_confidence(geolocator, reviews, config.gmaps_radius)
        logger.trace(f"\n[+] Probable location (confidence => {confidence}) :")
        loc_names = []
        for loc in locations:
            loc_names.append(f"- {loc['avg']['town']}, {loc['avg']['country']}")

        loc_names = set(loc_names)  # delete duplicates
        account_info[f"Probable location (confidence => {confidence})"] = "\n".join(loc_names)
        for loc in loc_names:
            logger.trace(loc)


async def get_profile_pic_and_youtube(client, account, account_info, email, name, infos):
    profile_pic_flathash = await get_profile_pic(client, account, account_info, email)
    await get_youtube(client, name, account_info, infos, profile_pic_flathash)


async def email_hunt(email):
    info_data = collections.OrderedDict()
    if not email:
        logger.critical("Please give a valid email.\nExample : larry@google.com")
        return

    hangouts_auth, hangouts_token, internal_auth, internal_token, cookies = config.data

    # client = httpx.Client(cookies=cookies, headers=config.headers)
    async with httpx.AsyncClient(cookies=cookies, headers=config.headers) as client:

        try:
            data = await is_email_google_account(client, hangouts_auth, cookies, email, hangouts_token)
        except (CookieExpiredError, FileNotFoundError, NotGoogleAccountError) as e:
            raise e

        geolocator = Nominatim(user_agent="nominatim")

        # info_data["acc_count"] = data['matches']
        info_data["accounts"] = []
        logger.trace(f"[+] {len(data['matches'])} account found !")

        account_info = {}

        for user in data["matches"]:
            logger.trace("\n------------------------------\n")

            gaiaID = user["personId"][0]
            email = user["lookupId"]
            infos = data["people"][gaiaID]

            # get name & profile picture
            # todo 25.03.2022 16:53 taima:
            account = await get_account_data(client, gaiaID, internal_auth, internal_token, config)
            name = account["name"]
            if name:
                account_info["Name"] = name
                logger.trace(f"Name : {name}")
            else:
                if "name" not in infos:
                    # account_info["name"] = None
                    logger.trace("[-] Couldn't find name")
                else:
                    for i in range(len(infos["name"])):
                        if "displayName" in infos["name"][i].keys():
                            name = infos["name"][i]["displayName"]
                            account_info["Name"] = name
                            logger.trace(f"Name : {name}")

            organizations = account["organizations"]
            if organizations:
                account_info["Organizations"] = organizations
                logger.trace(f"Organizations : {organizations}")

            locations = account["locations"]
            if locations:
                account_info["Locations"] = organizations
                logger.trace(f"Locations : {locations}")

            await asyncio.gather(
                get_profile_pic_and_youtube(client, account, account_info, email, name, infos),
                get_cover_profile_pic(client, account, account_info, email),
                get_last_edit(account_info, infos),
                get_email(account, account_info, infos, email, gaiaID),
                is_bot(account_info, infos),
                get_reviews(client, account_info, gaiaID, cookies, geolocator),
                get_calendar(client, account_info, email),
            )

            # check YouTube
            # profile picture
            # await get_profile_pic(client, account, account_info, email)
            # await get_profile_pic(client, name, account_info, infos, profile_pic_flathash)

            # profile picture and check YouTube
            # await get_profile_pic_and_youtube(client, account, account_info, email, name, infos)
            #
            # # cover profile picture
            # await get_cover_profile_pic(client, account, account_info, email)
            #
            # # last edit
            # await get_last_edit(account_info, infos)
            #
            # # email & gaida id
            # await get_email(account, account_info, infos, email, gaiaID)
            #
            # # is bot?
            # await is_bot(account_info, infos)
            #
            # # TODO: return gpics function output here
            # # gpics(gaiaID, client, cookies, config.headers, config.regexs["albums"], config.regexs["photos"],
            # #      config.headless)
            #
            # # reviews
            # await get_reviews(client, account_info, gaiaID, cookies, geolocator)
            #
            # # Google Calendar
            # await get_calendar(client, account_info, email)

            info_data["accounts"].append(account_info)

        return info_data
