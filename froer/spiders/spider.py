import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FroerItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class FroerSpider(scrapy.Spider):
	name = 'froer'
	start_urls = ['https://www.froerupandelskasse.dk/nyheder/?page=1']

	def parse(self, response):
		post_links = response.xpath('//a[@class="read-more"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//ul[@class="paging"]/li[last()]/a/@href').get()
		if int(next_page.split('=')[1]) < len(response.xpath('//ul[@class="paging"]/li/a').get()):
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//span[@class="post-date"]/text()').get()
		title = response.xpath('//h1[@class="post-title"]/text()').get()
		subtitle = response.xpath('//h3[@class="post-sub-title"]/text()').get()
		if subtitle:
			title = title + subtitle
		content = response.xpath('//div[@class="post"]/p//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FroerItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
