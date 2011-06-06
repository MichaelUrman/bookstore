from django import template
register = template.Library()

import datetime
today = datetime.date.today
now = datetime.datetime.now
oneday = datetime.timedelta(1)

@register.filter
def bookpublished(book):
    return book.publish_date >= today()
    
@register.filter
def purchaseexpired(purchase):
    return purchase.date + oneday < now()

@register.filter
def count(value, limit=None):
    if value:
        return value.count(limit)
    return 0

@register.filter
def timespan(value):
    seconds = value.seconds
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    pieces = []
    if value.days:
        pieces.append("%d days" % value.days)
    if hours:
        pieces.append("%d hours" % hours)
    if minutes:
        pieces.append("%d minutes" % minutes)
    return ', '.join(pieces)

@register.filter
def youtube(value, size):
    x, y = size.split('x')
    return ('<object width="%(x)s" height="%(y)s">'
        '<param name="movie" value="http://www.youtube.com/v/%(vid)s&amp;hl=en_US&amp;fs=1&amp;color1=0x3a3a3a&amp;color2=0x999999&amp;border=1">'
        '<param name="allowFullScreen" value="true">'
        '<param name="allowscriptaccess" value="always">'
        '<embed type="application/x-shockwave-flash" width="%(x)s" height="%(y)s" src="http://www.youtube.com/v/%(vid)s&amp;hl=en_US&amp;fs=1&amp;color1=0x3a3a3a&amp;color2=0x999999&amp;border=1" allowscriptaccess="always" allowfullscreen="true" />'
        '</object>' % dict(x=x, y=y, vid=value))
        
@register.filter
def chain(value, next):
    for v in value: yield v
    for v in next: yield v
    
@register.filter
def imageblob(value, size=None):
    return get_serving_url(str(value.key()), size and int(size))
    
@register.filter
def ppattrs(value, name=None):
    if name:
        return getattr(value, name)
    return set([attr for attr in dir(value) if attr.startswith('pp_')] + 'pp_business pp_charset pp_first_name pp_handling_amount pp_handling_amount pp_invoice pp_last_name pp_item_name pp_mc_currency pp_mc_fee pp_mc_gross pp_notify_version pp_payer_email pp_payer_id pp_payer_status pp_payment_date pp_payment_fee pp_payment_gross pp_payment_status pp_payment_type pp_protection_eligibility pp_quantity pp_receiver_email pp_receiver_id pp_residence_country pp_shipping pp_tax pp_transaction_subject pp_txn_id pp_txn_type pp_verify_sign'.split())
        
@register.simple_tag
def wallpapers(wall, aspects):
    pieces = []
    for aspect in aspects:
        if aspect.ratio == wall.aspect:
            for size in aspect:
                w, h = map(int, size.split('x'))
                if w == wall.width and h == wall.height:
                    pieces.append('<a href="/image/wall/%s">%s</a>' % (wall.key(), size));
                elif w <= wall.width and h <= wall.height:
                    pieces.append('<a href="%s">%s</a>' % (get_serving_url(str(wall.image.key()), w), size))
    return ''.join(pieces)
        
@register.simple_tag
def pager(info):
    if info.pagecount < 2:
        return ''
    pieces = [
        '<div id="pager"><span class="pager ui-corner-all">',
        info.prev and ('<a href="%s" title="Previous Page">&laquo;</a>' % info.prev) or '&laquo;',
        info.next and ('<a href="%s" title="Next Page">&raquo;</a>' % info.next) or '&raquo;',
        '</span></div>',
        '<!-- %d @ %d -->' % (info.size, info.offset),
        ]
    pieces[2:2] = [ (i == info.page and '<span class="current" title="Page %(i1)d">&bull;</span>'
        or  '<a href="?p=%(i0)d%(sizer)s" title="Page %(i1)d">&bull;</a>') % dict(i0=i, i1=i+1, sizer=info.sizer)
        for i in range(info.pagecount) ]
    return ''.join(pieces).encode('ascii', 'xmlcharrefreplace')

def set_of(items, template, empty='', first=', ', final=' &amp; '):
    pieces = map(template, items)
    if not pieces: return empty
    comma = first.join(pieces[:-1])
    if not comma: return pieces[0].encode('ascii', 'xmlcharrefreplace')
    return final.join([comma, pieces[-1]]).encode('ascii', 'xmlcharrefreplace')
    
@register.simple_tag
def authorsof(book, linkify=True):
    if linkify:
        template = lambda a: '<a href="/author/%s">%s %s</a>' % (a.link, a.firstname, a.lastname)
    else:
        template = lambda a: '%s %s' % (a.firstname, a.lastname)
    return set_of(book.authors.all(), template, '(nobody)')
        
@register.simple_tag
def genresof(book, linkify=True):
    if linkify:
        template = lambda g: '<a href="/genre/%s">%s</a>' % (g.link, g.name)
    else:
        template = lambda g: '%s' % (g.name)
    return set_of(book.genres.all(), template, '(none)')
        
