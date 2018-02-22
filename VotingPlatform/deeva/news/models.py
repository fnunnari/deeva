#NEWS models
from __future__ import unicode_literals

from django.db import models

# The news model with a title and a text in html format
class News(models.Model):
    from django.utils import timezone
    title = models.CharField(max_length = 128)
    text = models.TextField(help_text="To shorten the text preview at a particular point add [short] to the text.")
    date = models.DateTimeField(default = timezone.now)
    keep_on_homepage = models.BooleanField(default = False, help_text="If checked, the news will stay on the homepage even if it is not one of the most recent ones.")
    hide = models.BooleanField(default = False, help_text="If checked, the news will not be displayed to users.")

    def text_short(self):
        if "[short]" in self.text:
            return "{0}...".format(self.text.split("[short]")[0])
        else:
            return self.text

    def share_news(self):
        from django.utils.safestring import mark_safe
        from django.core.urlresolvers import reverse
        from django.contrib.sites.models import Site
        from django.utils.html import strip_tags

        current_site = Site.objects.get_current()
        """
        news_url = "{site}{path}#news_{id}".format(site=current_site, path=reverse('news'), id=self.id)

        strippedtext = "test " #strip_tags(self.text.replace('\n', '\\n').replace('\r', ''))

        twitter = '''<script>!function(d,s,id){{var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){{js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}}}(document, 'script', 'twitter-wjs');</script> <a href="https://twitter.com/share" class="twitter-share-button" data-url="{url}" data-text="{title} {url}">Tweet</a>'''.format(title=self.title, url=news_url)

        facebook = '''<script> window.fbAsyncInit = function() {{console.log('FB.init()');FB.init({{appId : '935180343184347',xfbml : true,version : 'v2.5'}});}};      (function(d, s, id){{var js, fjs = d.getElementsByTagName(s)[0];if (d.getElementById(id)) {{return;}}js = d.createElement(s); js.id =id; js.src = "//connect.facebook.net/en_US/sdk.js";fjs.parentNode.insertBefore(js, fjs);}}(document, 'script', 'facebook-jssdk'));</script> <a href="#bla" style="text-align:center; text-decoration: none; vertical-align:top;" onclick="console.log('lancio FB') ; FB.ui( {{ method: 'feed', link: '{url}', name: '{title}', description: '{text}', caption: 'DEEVA.MMCI.UNI-SAARLAND.DE', app_id: '935180343184347', picture:'http://deeva.mmci.uni-saarland.de/static/images/logo/Deeva-logo.png'}}, function(response){{console.log('risposta'); console.log(response) }} );"><img src="http://deeva.mmci.uni-saarland.de/static/images/FB-f-Logo__blue_72.png" height="20pt" /></a>'''.format(title=self.title, url=news_url, text=strippedtext)

        warning = '''<div id="change_warning">Save changes before sharing!</div><script>var counterv = 0;document.getElementById('change_warning').style.visibility = "hidden"; document.getElementById('id_text').onchange = function() {if (counterv++ == 0) {document.getElementById('change_warning').style.visibility = "visible";document.getElementById('change_warning').style.color = "red";}} </script>'''

        return  mark_safe("{}{}{}".format(twitter, facebook, warning))
        """
        return  mark_safe("TODO activate share buttons news/models.py")

    def __unicode__(self):
        return "{0} ({1})".format(self.title, self.date)

    class Meta:
        verbose_name_plural = "News"