import re

from .reddit_post import RedditPost
from .image_poll import ImagePoll, Image
from .straw_poll import StrawPollError, VotePass


class PollError(Exception):
    pass


class Polls:
	
	def __init__(self):
		self._map = {
			'reddit_image_poll'	: self._reddit_image_poll,
			'reddit_image_poll2'	 : self._reddit_image_poll2
		}


	def run(self, poll_name, params=None):
		if not poll_name in self._map.keys():
			print('no such poll')
			print('available polls:\n' + '\n'.join(self._map.keys()))
			return

		method = self._map[poll_name]
		try:
		    method(params)
		except PollError as e:
		    print(e)


	def _reddit_image_poll(self, params):
		j = self._get_reddit_post_content(params)

		list_item_regex = re.compile("\d+\.\s+\[(.*?)\]\((.*?)\).*\((.*?)\)")
		matches = list_item_regex.findall(j)

		for m in matches:
			ip = ImagePoll(title=m[0].strip(), images=Image(None, m[1].strip()), poll_url=m[2].strip(), cache_images=True)
			self._ip_vote()
	    

	def _get_reddit_post_content(self, params):
		if not 'post_id' in params.keys():
			raise PollError('please provide a reddit post id')

		rp = RedditPost(post_id=params['post_id'], cache=True)
		return rp.content


	def _ip_vote(self, ip):
		try:
			success = ip.vote()
			if not success:
				print('failure in casting vote')
		except VotePass:
			pass
		except StrawPollError as e:
			print(e)


	def _reddit_image_poll2(self, params):
		j = self._get_reddit_post_content(params)

		list_item_regex = re.compile("^\d+\..*$", re.M)
		matches = list_item_regex.findall(j)

		link_regex = re.compile("\[(.*?)\]\((.*?)\)")
		for m in matches:
			links = link_regex.findall(m)
			images = []
			for l in links[:-1]:
				img = Image(l[0].strip(), l[1].strip())
				images.append(img)

			ip = ImagePoll(title=links[0][0].strip(), images=images, poll_url=links[-1][1].strip(), cache_images=True)
			self._ip_vote(ip)
       
