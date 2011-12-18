from urllib import unquote

def fix_playpath(url):
	return url.replace('/mp4:', '/ -y mp4:')

service = [
		[
			{	'service-name':		'SVT-play',
			#	're'		:	r'(http://)?(www\.)?svtplay.se/(?P<url>.+)',
			#	'template'	:	'http://svtplay.se/%(url)s'},
				're'		:	r'(http://)?(www\.)?svtplay.se/(?P<path>(t|v)/\d+)',
				'template'	:	'http://svtplay.se/popup/minispelare/%(path)s'},
			#{	're'		:	r'(?:name="movie" value="(?P<swf_url>[^"]+)".*?)?(?P<url>rtmpe?://[^,]+),bitrate:(?P<bitrate>[0-9]+)',
			#{	're'		:	r'(?:name="movie" value="(?P<swf_url>[^"]+)".*subtitle=(?P<sub>[^&]+).*?)?(?P<url>rtmpe?://[^,]+),bitrate:(?P<bitrate>[0-9]+)',
			{	're'		:	r'(?:name="movie" value="(?P<swf_url>[^"]+)".*?)?(?P<url>rtmpe?://[^,]+),bitrate:(?P<bitrate>[0-9]+)(?=.*?subtitle=(?P<sub>[^&]*))',
				'template'	:	'#quality: %(bitrate)s kbps; subtitles: %(sub)s;\nrtmpdump --swfVfy http://svtplay.se%(swf_url)s -r %(url)s -o %(output_file)s'}],
		[#SVT-play-alternate/flv clip
			{	're'		:	r'(http://)?(www\.)?svtplay.se/(?P<url>.+)',
				'template'	:	'http://svtplay.se/%(url)s'},
			#{	're'		:	r'(http://)?(www\.)?svtplay.se/(?P<path>(t|v)/\d+)',
			#	'template'	:	'http://svtplay.se/popup/minispelare/%(path)s'},
			{	're'		:	r'pathflv=(?P<url>http?://[^&]+)',
				'template'	:	'#\n%(url)s'}],
		[#SVT-play-alternate/flv clip-rtmp
			{	're'		:	r'(http://)?(www\.)?svtplay.se/(?P<url>.+)',
				'template'	:	'http://svtplay.se/%(url)s'},
			{	're'		:	r'(?:name="movie" value="(?P<swf_url>[^"]+)".*?)pathflv=(?P<url>rtmpe?://[^&]+)',
				'template'	:	'#\nrtmpdump -W "http://svtplay.se%(swf_url)s" -r "%(url)s" -o %(output_file)s'}],
		[
			{	'service-name':		'SR',
				're'		:	r'(http://)?(www\.)?sverigesradio.se/(?P<url>.+)',
				'template'	:	'http://sverigesradio.se/%(url)s'},
			{	're'		:	r'<ref href="(?P<url>[^"]+)"',
				'template'	:	'#\n%(url)s'}],
		[
			{	'service-name':		'UR-play',
				're'		:	r'(http://)?(www\.)?urplay.se/(?P<url>.+)',
				'template'	:	'http://urplay.se/%(url)s'},
			{	're'		:	r'file=/(?P<url>[^&]+(?P<ext>mp[34]))(?:.*?captions.file=(?P<sub>[^&]+))?',
				'template'	:	'#subtitles: %(sub)s;\nrtmpdump -r rtmp://streaming.ur.se/ -y %(ext)s:/%(url)s -a ondemand -o %(output_file)s'}],
		[
			{	'service-name':		'TV4-play',
				're'		:	r'(http://)?(www\.)?tv4play.se/.*videoid=(?P<id>\d+).*',
				'template'	:	'http://premium.tv4play.se/api/web/asset/%(id)s/play'},
			{	're'		:	r'(<playbackStatus>(?P<status>\w+).*?)?<bitrate>(?P<bitrate>[0-9]+)</bitrate>.*?(?P<base>rtmpe?://[^<]+).*?(?P<url>mp4:/[^<]+)(?=.*?(?P<sub>http://anytime.tv4.se/multimedia/vman/smiroot/[^<]+))?',
				'template'	:	'#quality: %(bitrate)s kbps; subtitles: %(sub)s;\nrtmpdump -W http://www.tv4play.se/flash/tv4playflashlets.swf -r %(base)s -y %(url)s -o %(output_file)s'}],
		[
			{	'service-name':		'MTG',
				're'		:	r'(http://)?(www\.)?tv[368]play.se/.*(?:play/(?P<id>\d+)).*',
				'template'	:	'http://viastream.viasat.tv/PlayProduct/%(id)s'},
			{	're'		:	r'<SamiFile>(?P<sub>[^<]*).*<Video>.*<BitRate>(?P<bitrate>\d+).*?<Url><!\[CDATA\[(?P<url>rtmp[^\]]+)',
				'template'	:	'#quality: %(bitrate)s kbps; subtitles: %(sub)s;\nrtmpdump -W http://flvplayer-viastream-viasat-tv.origin.vss.viasat.tv/play/swf/player110420.swf -r %(url)s -o %(output_file)s',
				'decode':		fix_playpath}],
		[#MTG-alternate
			{	're'		:	r'(http://)?(www\.)?tv[368]play.se/.*(?:play/(?P<id>\d+)).*',
				'template'	:	'http://viastream.viasat.tv/PlayProduct/%(id)s'},
			{	're'		:	r'<SamiFile>(?P<sub>[^<]*).*<Video>.*<BitRate>(?P<bitrate>\d+).*?<Url><!\[CDATA\[(?P<url>http[^\]]+)',
				'template'	:	'%(url)s'},
			{	're'		:	r'<Url>(?P<url>[^<]+)',
				'template'	:	'#quality: %(bitrate)s kbps; subtitles: %(sub)s;\nrtmpdump -W http://flvplayer-viastream-viasat-tv.origin.vss.viasat.tv/play/swf/player110420.swf -r %(url)s -o %(output_file)s',
				'decode':		fix_playpath}],
		[
			{	'service-name':		'Aftonbladet-TV',
				're'		:	r'(http://)?(www\.)?aftonbladet.se/(?P<url>.+)',
				'template'	:	'http://aftonbladet.se/%(url)s'},
			{	're'		:	'videoUrl:\s"(?P<base>rtmp://(ss11i04.stream.ip-only.net|fl1.c00862.cdn.qbrick.com)/[^/]+/)(?P<url>[^"]+)"',
				'template'	:	'#\nrtmpdump -r "%(base)s" -y "%(url)s" -o "%(output_file)s"'}],
		[
			{
				'service-name':		'Vimeo',
				'headers':		{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.36 (KHTML, like Gecko) Chrome/13.0.766.0 Safari/534.36'},
				're'		:	r'(http://)?(www\.)?vimeo.com/.*?(?P<id>\d+)$',
				'template'	:	'http://vimeo.com/%(id)s'},
			{
				'headers':		{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.36 (KHTML, like Gecko) Chrome/13.0.766.0 Safari/534.36'},
				're'		:	r'"signature":"(?P<sig>[^"]+)".*?timestamp":(?P<time>\d+).*?h264":\["(?P<quality>[^"]+)',
				'template'	:	'http://player.vimeo.com/play_redirect?clip_id=%(id)s&sig=%(sig)s&time=%(time)s&quality=%(quality)s&codecs=H264,VP8,VP6&type=moogaloop_local&embed_location='},
			{
				'headers':		{'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.36 (KHTML, like Gecko) Chrome/13.0.766.0 Safari/534.36'},
				're'		:	r'Location: (?P<url>.*?)\n',
				'template'	:	'#quality: %(quality)s;\n%(url)s'}],
		[
			{	'service-name':		'Kanal5-play, Kanal9-play',
				're'		:	r'(http://)?(www\.)?kanal(?P<n>5|9)play.se/(?P<url>.+)',
				'template'	:	'http://kanal%(n)splay.se/%(url)s'},
			{	're'		:	r'@videoPlayer" value="(?P<video_player>[^"]+)"',
				'template'	:	'kanal5://%(video_player)s'},
			{
				're'		:	r'"(?P<height>\d+)x(?P<width>\d+):(?P<URL>[^&]+)&(?P<path>[^"]+)";',
				'template'	:	'#quality: %(height)sx%(width)s;\nrtmpdump --swfVfy http://admin.brightcove.com/viewer/us1.25.04.01.2011-05-24182704/connection/ExternalConnection_2.swf -r %(URL)s -y %(path)s -o %(output_file)s'}],
		[
			{	're':			r'(http://)?(www\.)?redtube.com/(?P<path>.+)',
				'template':		'http://redtube.com/%(path)s'},
			{	're':			'<source src="(?P<url>[^"]+)"',
				'template':		'#\n%(url)s'}],
		[
			{	'service-name':		'Axess-TV',
				're'		:	r'(http://)?(www\.)?axess.se/(?P<url>.+)',
				'template'	:	'http://axess.se/%(url)s'},
			{	're'		:	r'url: \'(?P<url>[^\']+)\'.*netConnectionUrl: \'(?P<base>[^\']+)',
				'template'	:	'#\nrtmpdump -r %(base)s -y %(url)s -o %(output_file)s'}],
		[
			{	'service-name':		'VGTV',
				're':			r'(http://)?(www\.)?vgtv.no/#!?id=(?P<id>\d+)',
				'template':		'http://www.vgtv.no/data/actions/videostatus/?id=%(id)s'},
			{	're':			r'"bitrate":(?P<bitrate>\d+).*?"address":"(?P<address>[^"]+)","port":80,"application":"","path":"download\\(?P<path1>[^\\]+)\\(?P<path2>[^\\]+).*?","filename":"(?P<filename>[^"]+)"',
				'template':		'#quality: %(bitrate)s\nhttp://%(address)s:80/download%(path1)s%(path2)s/vgtv/streaming/compressed/%(id)s/%(filename)s'}],
		[
			{	'service-name':		'ABF-play',
				're':			r'(http://)?(www\.)?abfplay.se/#(?P<id>.+)',
				'template':		'http://csp.picsearch.com/rest?jsonp=ps.responseHandler&eventParam=3&auth=r4MlmWY4CCH4AS_Z41gYqik4B37w5SQxkPkTiN2zCLqY8abCNEEDvA&method=embed&containerId=mediaplayer&mediaid=%(id)s&autoplay=true&player=rutile&width=620&height=430'},
			{	're':			r'"url": "rtmp%%3A//rtmp.picsearch.com/content/(?P<url>[^"]+)%%3F',
				'template':		'#\nrtmpdump -r rtmp://rtmp.picsearch.com/content -a content -W http://csp.picsearch.com/players/rutile.swf -y %(url)s -o %(output_file)s'}],
		[
			{	'service-name':		'Youtube',
				're':			r'(http://)?(www\.)?youtube.com/(?P<url>.+)',
				'template':		'http://youtube.com/%(url)s'},
			{	're':			r'url%%3D(?P<url>.*?)%%26quality%%3D(?P<quality>.*?)%%26',
				'template':		'#quality: %(quality)s\n%(url)s',
				'decode':		lambda url: unquote(unquote(url))}],
		[
			{	'service-name':		'NRK nett-TV',
				'headers':		{'Cookie': 'NetTV2.0Speed=7336'},
				're':			r'(http://)?(www\.)?nrk.no/nett-tv/(?P<url>.+)',
				'template':		'http://nrk.no/nett-tv/%(url)s'},
			{	're':			r'name="Url" value="(?P<url>[^"]+)',
				'template':		'%(url)s'},
			{	're':			r'href="(?P<url>mms://[^"]+)"',
				'template':		'#\n%(url)s'}],
		[
			{	'service-name':		'DR NU',
				're':			r'(http://)?(www\.)?dr\.dk/nu/player/#/(?P<title>[^/]+)/(?P<id>\d+).*',
				'template':		'http://www.dr.dk/nu/api/programseries/%(title)s/videos'},
			{
				're':			r'"id": %(id)s,[^}]+"videoResourceUrl": "(?P<url>[^"]+)"',
				'template':		'%(url)s'},
			{
				're':			r'uri":"(?P<uri>[^"]+)".*?"bitrateKbps":(?P<bitrate>\d+)',
				'template':		'#quality: %(bitrate)s\nrtmpdump -r %(uri)s -W http://www.dr.dk/nu/assets/swf/NetTVPlayer_10.swf',
				'decode':		lambda url: fix_playpath(url.replace('\\', ''))}],
		[
			{	'service-name':		'Ceskatelevize',
				're':			r'(http://)?(www\.)?ceskatelevize\.cz/(?P<url>.+)',
				'template':		'http://www.ceskatelevize.cz/%(url)s'},
			{	're':			'IDEC="(?P<identifier>[^"]+)"',
				'template':		'http://www.ceskatelevize.cz/ajax/playlistURL.php',
				'post-template':	'options%%5BuserIP%%5D=85.226.8.253&options%%5BplayerType%%5D=flash&options%%5BplaylistItems%%5D%%5B0%%5D%%5BType%%5D=Ad&options%%5BplaylistItems%%5D%%5B0%%5D%%5BFormat%%5D=MP4_Web&options%%5BplaylistItems%%5D%%5B0%%5D%%5BIdentifier%%5D=AD-46&options%%5BplaylistItems%%5D%%5B0%%5D%%5BTitle%%5D=Reklama%%3A+Adventn%%C3%%AD+kalend%%C3%%A1%%C5%%99&options%%5BplaylistItems%%5D%%5B0%%5D%%5BSkip%%5D%%5BEnable%%5D=true&options%%5BplaylistItems%%5D%%5B0%%5D%%5BSkip%%5D%%5BDelay%%5D=3&options%%5BplaylistItems%%5D%%5B0%%5D%%5BClickThruURL%%5D=http%%3A%%2F%%2Fadvent.ceskatelevize.cz%%2F&options%%5BplaylistItems%%5D%%5B1%%5D%%5BType%%5D=Archive&options%%5BplaylistItems%%5D%%5B1%%5D%%5BFormat%%5D=MP4_Web&options%%5BplaylistItems%%5D%%5B1%%5D%%5BIdentifier%%5D=%(identifier)s&options%%5BplaylistItems%%5D%%5B1%%5D%%5BTitle%%5D=Vypr%%C3%%A1v%%C4%%9Bj&options%%5BplaylistItems%%5D%%5B1%%5D%%5BRegion%%5D=&options%%5BplaylistItems%%5D%%5B1%%5D%%5BSubtitlesUrl%%5D=http%%3A%%2F%%2Fimg7.ceskatelevize.cz%%2Fivysilani%%2Fsubtitles%%2F211%%2F211522161400013%%2Fsubtitles-1.txt&options%%5BplaylistItems%%5D%%5B1%%5D%%5BIndexes%%5D=null&options%%5BpreviewImageURL%%5D=http%%3A%%2F%%2Fimg7.ceskatelevize.cz%%2Fcache%%2F512x288%%2Fivysilani%%2Fepisodes%%2Fphotos%%2Fw512%%2F10195164142%%2F1-62384.jpg'},
			{	're':			'(?P<playlist_url>.+)',
				'template':		'%(playlist_url)s',
				'headers':		{'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:5.0) Gecko/20100101 Firefox/5.0'}},
			{	're':			r'(base="(?P<base>rtmp://[^/]+/)(?P<app>[^"]+)".*?)?src="(?P<play_path>[^"]+)".*?label="(?P<quality>[^"]+)"',
				'template':		'#quality: %(quality)s\nrtmpdump -r "%(base)s" -a "%(app)s" -y "%(play_path)s" -W "http://img7.ceskatelevize.cz/libraries/player/flashPlayer.swf?version=1.44.5"',
				'headers':		{'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:5.0) Gecko/20100101 Firefox/5.0'},
				'decode':		lambda url: url.replace('&amp;', '&')}]]