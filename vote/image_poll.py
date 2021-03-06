from os.path import join as joinpath, exists
from os import mkdir
from subprocess import run

import requests
from redlib.api.system import sys_command, is_windows, is_linux

from .straw_poll import StrawPoll


class Image:

	def __init__(self, title, url):
	    self.title	= title
	    self.url	= url


class ImagePoll:
	cache_folder = 'image_cache'


	def __init__(self, title, poll_url, cache_images=True, cache_folder=None, images=None):
		self._title	= title
		self._poll_url	= poll_url
		self._images	= images

		self._cache_images = cache_images
		self._cache_folder = cache_folder or self.cache_folder

		self._strawpoll = StrawPoll()


	def vote(self):
		print(self._title)
		poll_id = self._poll_url.split('/')[-1]

		if self._strawpoll.already_voted(poll_id):
			print('already voted')
			return True
			
		if self._images is not None:
			for image in self._images:
				if image.title is not None:
					print(image.title)
				try:
					filepath = self._download_image(image.url)
					self._show_image(filepath)
				except KeyboardInterrupt:
					print('skipping..')	

		return self._strawpoll.vote(poll_id)


	def _show_image(self, filepath):
		if is_windows():
			sys_command("cmd /c start %s"%filepath)
		elif is_linux():
			run(("xdg-open %s"%filepath).split())
		else:
			print('unsupported OS')
		

	def _download_image(self, url):
		filename = url.split('/')[-1]
		filepath = self._lookup_cache(filename)
		if filepath is not None:
			return filepath

		print('getting image: %s'%url)
		response = requests.get(url)

		if not self._cache_images:
			return self._save_image(response.content, filename)
		else:
			return self._cache_image(response.content, filename)


	def _save_image(self, data, filename):
		with open(filename, 'wb') as f:
			f.write(data)

		return filename


	def _cache_image(self, data, filename):
		if not exists(self._cache_folder):
			mkdir(self._cache_folder)

		filepath = joinpath(self.cache_folder, filename)

		with open(filepath, 'wb') as f:
			f.write(data)

		return filepath


	def _lookup_cache(self, filename):
		filepath = joinpath(self.cache_folder, filename)
		if exists(filepath):
			return filepath
		else:
			return None
