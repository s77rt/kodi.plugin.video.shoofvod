# -*- coding: utf8 -*-
import urllib.request, urllib.parse, http.client
import xbmc, xbmcgui, xbmcplugin
import re

__url__ = sys.argv[0]
__handle__ = int(sys.argv[1])

WEBSITE = 'http://shoofvod.com'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'

class Pagination(object):
	def __init__(self, url=''):
		super(Pagination, self).__init__()
		self.url = str(url)
		self.set_current_page(str(url))
	def set_current_page(self, url):
		page_regex = re.search(r'Cat-\d+-(\d+)', url)
		if page_regex:
			self.current_page = int(page_regex.group(1))
			return
		page_regex = re.search(r'al_\d+_(\d+)', url)
		if page_regex:
			self.current_page = int(page_regex.group(1))
			return
		page_regex = re.search(r'Search\/.+\/(\d+)', url)
		if page_regex:
			self.current_page = int(page_regex.group(1))
			return
		self.current_page = 0
		return
	def next_page(self, step=1):
		if self.current_page <= 0:
			return None
		return urllib.parse.quote(re.sub(r'(\-|\_|\/)'+str(re.escape(str(self.current_page)))+'$', r'\1'+'#X#'+str(re.escape(str(self.current_page+step))), self.url).replace('#X#', ''))
	def previous_page(self, step=1):
		if self.current_page <= 1:
			return None
		return urllib.parse.quote(re.sub(r'(\-|\_|\/)'+str(re.escape(str(self.current_page)))+'$', r'\1'+'#X#'+str(re.escape(str(self.current_page-step))), self.url).replace('#X#', ''))
	def goto_page(self, page):
		if page <= 0:
			return None
		return urllib.parse.quote(re.sub(r'(\-|\_|\/)'+str(re.escape(str(self.current_page)))+'$', r'\1'+'#X#'+str(re.escape(str(page))), self.url).replace('#X#', ''))

_Pagination = Pagination()

def get_categories():
	req = urllib.request.Request(WEBSITE)
	req.add_header('User-Agent', UA)
	try:
		response = urllib.request.urlopen(req)
	except http.client.IncompleteRead as e:
		response = e.partial
	data = response.read()
	categories = re.findall(r'<a\s+href="(\/Cat.*?)">([^<]*)?<\/a>', data.decode('utf-8'), re.DOTALL|re.MULTILINE)
	global _Pagination
	_Pagination = Pagination()
	return categories

def get_subcategories(category):
	req = urllib.request.Request(WEBSITE+category)
	req.add_header('User-Agent', UA)
	try:
		response = urllib.request.urlopen(req)
	except http.client.IncompleteRead as e:
		response = e.partial
	data = response.read().decode('utf-8')
	albums_url_n_thumb = re.findall(r'[^>]<a\s+href="(\/al_.*?)">\s+<div.*?\s+<img\s+src="(.*?)"', data, re.DOTALL|re.MULTILINE)
	albums_name = re.findall(r'<div\s+class="title"><h4>([^<]*)<\/h4><\/div>', data, re.DOTALL|re.MULTILINE)
	albums = []
	for i in range(len(albums_url_n_thumb)):
		try:
			albums.append((albums_url_n_thumb[i][0], albums_name[i], albums_url_n_thumb[i][1]))
		except:
			pass
	global _Pagination
	_Pagination = Pagination(category)
	return albums

def get_videos(category):
	req = urllib.request.Request(WEBSITE+category)
	req.add_header('User-Agent', UA)
	try:
		response = urllib.request.urlopen(req)
	except http.client.IncompleteRead as e:
		response = e.partial
	data = response.read().decode('utf-8')
	videos_url_n_thumb = re.findall(r'<a\s+href="(\/vidpage_.*?)">\s+<img\s+src="(.*?)"', data, re.DOTALL|re.MULTILINE)
	videos_name = re.findall(r'<div\s+class="title"><h4>([^<]*)<\/h4><\/div>', data, re.DOTALL|re.MULTILINE)
	videos_genre = re.findall(r'<h1>([^<]*)<\/h1>', data, re.DOTALL|re.MULTILINE)[0]
	videos = []
	for i in range(len(videos_url_n_thumb)):
		try:
			videos.append({
				'url': videos_url_n_thumb[i][0],
				'thumb': videos_url_n_thumb[i][1],
				'name': videos_name[i],
				'genre': videos_genre,
			})
		except:
			pass
	global _Pagination
	_Pagination = Pagination(category)
	return videos

def search(q=None, page=1, qs=None):
	if not q and not qs:
		return None
	if not qs:
		qs = '/Search/{}/{}'.format(urllib.parse.quote(q), page)
	req = urllib.request.Request(WEBSITE+qs)
	req.add_header('User-Agent', UA)
	try:
		response = urllib.request.urlopen(req)
	except http.client.IncompleteRead as e:
		response = e.partial
	data = response.read().decode('utf-8')
	videos_url_n_thumb = re.findall(r'<a\s+href="(\/vidpage_.*?)">\s+<img\s+src="(.*?)"', data, re.DOTALL|re.MULTILINE)
	videos_name = re.findall(r'<div\s+class="title"><h4>([^<]*)<\/h4><\/div>', data, re.DOTALL|re.MULTILINE)
	videos_genre = re.findall(r'<h1>([^<]*)<\/h1>', data, re.DOTALL|re.MULTILINE)[0]
	videos = []
	for i in range(len(videos_url_n_thumb)):
		try:
			videos.append({
				'url': videos_url_n_thumb[i][0],
				'thumb': videos_url_n_thumb[i][1],
				'name': videos_name[i],
				'genre': videos_genre,
			})
		except:
			pass
	global _Pagination
	_Pagination = Pagination(qs)
	return videos

def get_video_src(video_url):
	video_src = ''
	try:
		phase1_url = WEBSITE+'/Play'+video_url.replace('vidpage_', '')
		phase1_req = urllib.request.Request(phase1_url)
		phase1_req.add_header('User-Agent', UA)
		try:
			phase1_response = urllib.request.urlopen(phase1_req)
		except http.client.IncompleteRead as e:
			phase1_response = e.partial
		phase1_data = phase1_response.read()
		phase2_url = "http://" + re.search(r'<iframe\s+src="(.*?)"', phase1_data.decode('utf-8'), re.DOTALL|re.MULTILINE).group(1).replace('https://', '').replace('http://', '').replace('//', '').replace(' ', '%20')
		phase2_req = urllib.request.Request(phase2_url)
		phase2_req.add_header('User-Agent', UA)
		try:
			phase2_response = urllib.request.urlopen(phase2_req)
		except http.client.IncompleteRead as e:
			phase2_response = e.partial
		phase2_data = phase2_response.read()
		video_src = "http://" + re.search(r'<source\s+src="\/?\/?(.*?)"', phase2_data.decode('utf-8'), re.DOTALL|re.MULTILINE).group(1).replace('https://', '').replace('http://', '').replace('//', '').replace(' ', '%20')
	except:
		pass
	return video_src

def list_categories(categories=None):
	xbmcplugin.setContent(__handle__, 'videos')
	listing = []
	global _Pagination
	if _Pagination.previous_page() is not None:
		list_item = xbmcgui.ListItem(label='PREVIOUS PAGE ({})'.format(_Pagination.current_page - 1))
		url = '{0}?action=listing&category={1}'.format(__url__, _Pagination.previous_page())
		is_folder = True
		listing.append((url, list_item, True))
		if _Pagination.current_page - 1 != 1:
			list_item = xbmcgui.ListItem(label='FIRST PAGE')
			url = '{0}?action=listing&category={1}'.format(__url__, _Pagination.goto_page(1))
			is_folder = True
			listing.append((url, list_item, True))
	if not categories:
		xbmcplugin.setPluginCategory(__handle__, 'ShoofVod Categories')
		categories = get_categories()
		for category in categories:
			list_item = xbmcgui.ListItem(label=category[1])
			list_item.setInfo('video', {'title': category, 'genre': category[1]})
			url = '{0}?action=listing&category={1}'.format(__url__, category[0])
			is_folder = True
			listing.append((url, list_item, is_folder))
	else:
		xbmcplugin.setPluginCategory(__handle__, 'ShoofVod Sub-Categories')
		for category in categories:
			list_item = xbmcgui.ListItem(label=category[1])
			list_item.setInfo('video', {'title': category, 'genre': category[1]})
			list_item.setArt({ 'poster': category[2], 'banner' : category[2] })
			url = '{0}?action=listing&category={1}'.format(__url__, category[0])
			is_folder = True
			listing.append((url, list_item, is_folder))
	if _Pagination.next_page() is not None:
		list_item = xbmcgui.ListItem(label='NEXT PAGE ({})'.format(_Pagination.current_page + 1))
		url = '{0}?action=listing&category={1}'.format(__url__, _Pagination.next_page())
		is_folder = True
		listing.append((url, list_item, True))
		list_item = xbmcgui.ListItem(label='SKIP 5 PAGES ({})'.format(_Pagination.current_page + 5))
		url = '{0}?action=listing&category={1}'.format(__url__, _Pagination.next_page(step=5))
		is_folder = True
		listing.append((url, list_item, True))
	xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
	xbmcplugin.endOfDirectory(__handle__)

def list_videos(category):
	xbmcplugin.setPluginCategory(__handle__, 'ShoofVod (@{})'.format(category))
	xbmcplugin.setContent(__handle__, 'videos')
	videos = get_videos(category)
	listing = []
	global _Pagination
	if _Pagination.previous_page() is not None:
		list_item = xbmcgui.ListItem(label='PREVIOUS PAGE ({})'.format(_Pagination.current_page - 1))
		url = '{0}?action=listing&category={1}'.format(__url__, _Pagination.previous_page())
		is_folder = True
		listing.append((url, list_item, True))
		if _Pagination.current_page - 1 != 1:
			list_item = xbmcgui.ListItem(label='FIRST PAGE')
			url = '{0}?action=listing&category={1}'.format(__url__, _Pagination.goto_page(1))
			is_folder = True
			listing.append((url, list_item, True))
	for video in videos:
		list_item = xbmcgui.ListItem(label=video['name'])
		list_item.setInfo('video', {'title': video['name'], 'genre': video['genre']})
		list_item.setArt({ 'poster': video['thumb'], 'banner' : video['thumb'] })
		list_item.setProperty('fanart_image', video['thumb'])
		list_item.setProperty('IsPlayable', 'true')
		url = '{0}?action=play&url={1}'.format(__url__, video['url'])
		is_folder = False
		listing.append((url, list_item, is_folder))
	if _Pagination.next_page() is not None:
		list_item = xbmcgui.ListItem(label='NEXT PAGE ({})'.format(_Pagination.current_page + 1))
		url = '{0}?action=listing&category={1}'.format(__url__, _Pagination.next_page())
		is_folder = True
		listing.append((url, list_item, True))
		list_item = xbmcgui.ListItem(label='SKIP 5 PAGES ({})'.format(_Pagination.current_page + 5))
		url = '{0}?action=listing&category={1}'.format(__url__, _Pagination.next_page(step=5))
		is_folder = True
		listing.append((url, list_item, True))
	xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
	xbmcplugin.endOfDirectory(__handle__)

def list_search_results(q=None, page=1, qs=None):
	if not q and not qs:
		q = xbmcgui.Dialog().input(heading='Search for:', type=xbmcgui.INPUT_ALPHANUM)
	if not q and not qs:
		return None
	if not q:
		xbmcplugin.setPluginCategory(__handle__, 'ShoofVod (Search: {})'.format(urllib.parse.quote(re.sub(r'\/Search\/(.+)\/.*', r'\1', qs))))
	else:
		xbmcplugin.setPluginCategory(__handle__, 'ShoofVod (Search: {})'.format(urllib.parse.quote(q)))
	xbmcplugin.setContent(__handle__, 'videos')
	videos = search(q, page, qs)
	listing = []
	global _Pagination
	if _Pagination.previous_page() is not None:
		list_item = xbmcgui.ListItem(label='PREVIOUS PAGE ({})'.format(_Pagination.current_page - 1))
		url = '{0}?action=search&qs={1}'.format(__url__, _Pagination.previous_page())
		is_folder = True
		listing.append((url, list_item, True))
		if _Pagination.current_page - 1 != 1:
			list_item = xbmcgui.ListItem(label='FIRST PAGE')
			url = '{0}?action=listing&category={1}'.format(__url__, _Pagination.goto_page(1))
			is_folder = True
			listing.append((url, list_item, True))
	for video in videos:
		list_item = xbmcgui.ListItem(label=video['name'])
		list_item.setInfo('video', {'title': video['name'], 'genre': video['genre']})
		list_item.setArt({ 'poster': video['thumb'], 'banner' : video['thumb'] })
		list_item.setProperty('fanart_image', video['thumb'])
		list_item.setProperty('IsPlayable', 'true')
		url = '{0}?action=play&url={1}'.format(__url__, video['url'])
		is_folder = False
		listing.append((url, list_item, is_folder))
	if _Pagination.next_page() is not None:
		list_item = xbmcgui.ListItem(label='NEXT PAGE ({})'.format(_Pagination.current_page + 1))
		url = '{0}?action=search&qs={1}'.format(__url__, _Pagination.next_page())
		is_folder = True
		listing.append((url, list_item, True))
		list_item = xbmcgui.ListItem(label='SKIP 5 PAGES ({})'.format(_Pagination.current_page + 5))
		url = '{0}?action=search&qs={1}'.format(__url__, _Pagination.next_page(step=5))
		is_folder = True
		listing.append((url, list_item, True))
	xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
	xbmcplugin.endOfDirectory(__handle__)

def play_video(path):
	play_item = xbmcgui.ListItem(path=path)
	xbmcplugin.setResolvedUrl(__handle__, True, listitem=play_item)

def main_menu():
	listing = []
	
	list_item = xbmcgui.ListItem(label='Browse ShoofVod')
	url = '{0}?action=browse'.format(__url__)
	listing.append((url, list_item, True))
	
	list_item = xbmcgui.ListItem(label='Search on ShoofVod')
	url = '{0}?action=search'.format(__url__)
	listing.append((url, list_item, True))

	xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
	xbmcplugin.endOfDirectory(__handle__)

def router(paramstring):
	parsed_paramstring = urllib.parse.urlparse('?'+paramstring[1:])
	params = dict(urllib.parse.parse_qsl(parsed_paramstring.query))
	if params:
		if params['action'] == 'browse':
			list_categories()
		elif params['action'] == 'search':
			if params.get('qs'):
				list_search_results(qs=params['qs'])
			elif params.get('q') and params.get('page'):
				list_search_results(q=params['q'], page=params['page'])
			elif params.get('q'):
				list_search_results(q=params['q'])
			else:
				list_search_results()
		elif params['action'] == 'listing':
			subcategories = get_subcategories(params['category'])
			if subcategories:
				list_categories(subcategories)
			else:
				list_videos(params['category'])
		elif params['action'] == 'play':
			play_video(get_video_src(params['url']))
	else:
		main_menu()

if __name__ == '__main__':
	router(sys.argv[2])
