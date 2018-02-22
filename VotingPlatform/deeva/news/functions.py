from .models import News

def getNews(limit=None, keepOnHome=True, short=False):
    """Returns an array of news objects

    limit -- numbers of recent news to be returned (None for all)
    keepOnHome -- if True add all news that should be kept on the homepage even if its more than the limit
    short -- wether the news should be cut off at the [short] marker or not
    """

    #get all news that are not hidden and order them by date
    newss = News.objects.filter(hide=False).order_by('-date')

    #only display recent number of news if desired
    if limit:
        newss = newss[:limit]

    #reinsert news that should be always visible
    if keepOnHome:
        #inconvenient solution, because MySQL doesn't support combine after slice
        kept_newss = News.objects.filter(hide=False, keep_on_homepage=True)
        id_list = list(newss.values_list('id', flat=True)) + list(kept_newss.values_list('id', flat=True))
        newss = News.objects.filter(id__in=id_list).order_by('-date')

    #cut text after short if wanted
    if short:
        for news in newss:
            news.text = news.text_short()

    #populate additional fields
    from django.core.urlresolvers import reverse
    for news in newss:
        news.url = reverse('oneNews', args=[news.id])
        news.fb_code = 'TODO facebook'
        news.twitter_code = 'TODO twitter'

    return newss



def getOneNews(id):
    """Returns one specific news object

    id -- id of the news to be returned
    """

    #get news
    try:
        news = News.objects.get(id=id)
    except News.DoesNotExist as e:
        raise e
    

    #populate additional fields
    news.url = 'TODO URL'
    news.fb_code = 'TODO facebook'
    news.twitter_code = 'TODO twitter'

    return news

