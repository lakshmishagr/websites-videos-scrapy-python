import os
from scrapy.crawler import CrawlerProcess
# from page_scraping.spiders.Abp import AbpLive
# from page_scraping.spiders.Abpdemo import Abp
from page_scraping.spiders.PuneMirror import PuneMirror
from page_scraping.spiders.Zeenews import Zeenews
from page_scraping.spiders.Wion import Wion
from page_scraping.spiders.IndiaCom import IndiaCom
from page_scraping.spiders.IndiaToday import IndiaToday
from page_scraping.spiders.IndianTimes import IndianTimes
from page_scraping.spiders.TimesNownews import TimesNownews
from page_scraping.spiders.Bgr import Bgr
from page_scraping.spiders.Dna import Dna
# from page_scraping.spiders.BollywoodLife import BollywoodLife
# from page_scraping.spiders.CricketCountry import CricketCountry
from page_scraping.spiders.BangaloreMirror import BangaloreMirror
from page_scraping.spiders.EconomicsTimes import EconomicsTimes
from page_scraping.spiders.EntertainmentTimes import EntertainmentTimes
from page_scraping.spiders.MissKyra import MissKyra
from page_scraping.spiders.MumbaiMirror import MumbaiMirror
from page_scraping.spiders.Ndtv import Ndtv
from page_scraping.spiders.NdtvDoctor import NdtvDoctor
from page_scraping.spiders.NdtvFood import NdtvFood
from page_scraping.spiders.NdtvGadgets import NdtvGadgets
# from page_scraping.spiders.NdtvMojarto import NdtvMojarto
from page_scraping.spiders.NdtvMovies import NdtvMovies
from page_scraping.spiders.NdtvSports import NdtvSports
from page_scraping.spiders.NdtvSwirlster import NdtvSwirlster
from page_scraping.spiders.TimesFood import TimesFood #dns error
from page_scraping.spiders.TimesOfIndia import TimeOfIndia
from page_scraping.spiders.VijayaKarnataka import VijayaKarnataka
from page_scraping.spiders.EntertainmentTimesTv import EntertainmentTimesTv
from  page_scraping.spiders.EntertainmentTimesMusic import EntertainmentTimesMusic
from page_scraping.spiders.EntertainmentTimesLifestyle import EntertainmentTimesLifestyle
from  page_scraping.spiders.EntertainmentTimesPageants import EntertainmentTimesPageants
from  page_scraping.spiders.EntertainmentTimesEvents import EntertainmentTimesEvents
from  page_scraping.spiders.TimesCity import TimesCity
from  page_scraping.spiders.TimesSports import TimesSports
from page_scraping.spiders.TimesNownewsSub import TimesNownewsSub
from page_scraping.spiders.NdtvAuto import NdtvAuto
from page_scraping.spiders.BusinessToday import BusinessToday
from page_scraping.spiders.IGN import IGN
from page_scraping.spiders.iDiva import iDiva
from page_scraping.spiders.BgrHindi import BgrHindi
from page_scraping.spiders.TheHealthSite import TheHealthSite
from page_scraping.spiders.BollywoodHungamaEng import BollywoodHungamaEng
from page_scraping.spiders.BusinessToday import BusinessToday
from page_scraping.spiders.Aajtak import Aajtak
from page_scraping.spiders.BusinessInsider import BusinessInsider
from page_scraping.spiders.GadgetsNow import GadgetsNow
# from page_scraping.spiders.UrduNews18 import UrduNews18
# from page_scraping.spiders.TamilNews18 import TamilNews18
# from page_scraping.spiders.PunjabNews18 import PunjabNews18
# from page_scraping.spiders.News18 import News18
# from page_scraping.spiders.MarathiNews import MarathiNews
# from page_scraping.spiders.MalayalamNews18 import MalayalamNews18
# from page_scraping.spiders.KannadaNews18 import KannadaNews18
# from page_scraping.spiders.GujaratiNews18 import GujaratiNews18
# from page_scraping.spiders.BengaliNews18 import BengaliNews18
from page_scraping.spiders.Hindustantimes import HT
from page_scraping.spiders.GadgetsNow import GadgetsNow
from scrapy.utils.project import get_project_settings
from slugify import slugify

# def scrapy_handler(event, context):
if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    # process.crawl(PuneMirror)
    # process.crawl(Zeenews)
    # process.crawl(Wion)
    # process.crawl(BusinessToday)
    # process.crawl(IndiaCom)
    # process.crawl(IndiaToday)
    # process.crawl(IndianTimes)
    # process.crawl(TimesNownews)

    # process.crawl(HT)
    # process.crawl(Bgr)
    # process.crawl(Dna)
    # process.crawl(BangaloreMirror)
    # process.crawl(EconomicsTimes)
    # process.crawl(EntertainmentTimes)
    # process.crawl(MissKyra)
    # process.crawl(iDiva)
    # process.crawl(IGN)
    # process.crawl(MumbaiMirror)
    # process.crawl(Ndtv)

    # process.crawl(NdtvDoctor)
    # process.crawl(NdtvFood)
    # process.crawl(NdtvGadgets)
    # process.crawl(NdtvMovies)
    # process.crawl(NdtvSports)
    # process.crawl(NdtvSwirlster)
    # process.crawl(NdtvAuto)
    # process.crawl(TimesFood)
    # process.crawl(TimeOfIndia)
    # process.crawl(VijayaKarnataka)
    # process.crawl(EntertainmentTimesTv)
    # process.crawl(EntertainmentTimesMusic)

    process.crawl(EntertainmentTimesLifestyle)
    process.crawl(EntertainmentTimesPageants)
    process.crawl(EntertainmentTimesEvents)
    process.crawl(TimesSports)
    process.crawl(TimesCity)
    process.crawl(BollywoodHungamaEng)
    process.crawl(TheHealthSite)
    process.crawl(BgrHindi)
    process.crawl(BusinessToday)
    process.crawl(Aajtak)
    process.crawl(GadgetsNow)
    process.crawl(TimesNownewsSub)

    # # process.crawl(CricketCountry)
    # # process.crawl(BollywoodLife)
    # # process.crawl(NdtvMojarto)
    # # process.crawl(AbpLive)
    # # process.crawl(Abp)
    # # process.crawl(UrduNews18)
    # # process.crawl(TamilNews18)
    # # process.crawl(PunjabNews18)
    # # process.crawl(News18)
    # # process.crawl(MarathiNews)
    # # process.crawl(MalayalamNews18)
    # # process.crawl(KannadaNews18)
    # # process.crawl(GujaratiNews18)
    # # process.crawl(BengaliNews18)
    process.start()

