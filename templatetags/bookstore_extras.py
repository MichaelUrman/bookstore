from django.utils.http import urlquote
from django import template
from django.template import Context
register = template.Library()

from bookstore.models import Genre, Person

import datetime
today = datetime.date.today
now = datetime.datetime.now
oneday = datetime.timedelta(1)

import re
_wiki_rules = [
    (re.compile(r"\&"), "&amp;"),    # html characters
    (re.compile(r"<"), "&lt;"),
    (re.compile(r">"), "&gt;"),
    (re.compile(r"\*([^*\s].*?[^*\s]|[^*\s])\*"), r"<strong>\1</strong>"),    # bold
    (re.compile(r"_([^_\s].*?[^_\s]|[^_\s])_"), r"<em>\1</em>"),    # italic
    (re.compile(r"\+([^+\s].*?[^+\s]|[^+\s])\+"), r"<u>\1</u>"),    # underline
    (re.compile(r"^!\s+(.*)$"), r"<h2>\1</h2>"),      # h2
    (re.compile(r"^!!\s+(.*)$"), r"<h3>\1</h3>"),     # h3
    (re.compile(r"^!!!\s+(.*)$"), r"<h4>\1</h4>"),    # h4
    (re.compile(r"^@center:!\s+(.*)$"), r"<h2 class='center'>\1</h2>"),   # h2
    (re.compile(r"^@center:!!\s+(.*)$"), r"<h3 class='center'>\1</h3>"),  # h3
    (re.compile(r"^@center:!!!\s+(.*)$"), r"<h4 class='center'>\1</h4>"), # h4
    (re.compile(r"^={4,}$"), "</div><div class='entry ui-corner-all'>"), # bubble
    (re.compile(r"^-{4,}$"), "<hr />"),      # hr
    (re.compile(r"---"), "&mdash;"),
    (re.compile(r"--"), "&ndash;"),
    (re.compile(r"^@center:\s+(.*)$"), r"<p class='center'>\1</p>"),  # center
    (re.compile(r"^@right:\s+(.*)$"), r"<p class='right'>\1</p>"),    # right
    (re.compile(r"^$"), "<br /><br />"),     # hacky paragraph
    (re.compile(r"\[a:(.*?)\]"), r"<a name='\1'></a>"), # named anchor
    (re.compile(r"\[go(to)?:(.*?)\|(.*?)\]"), r"<a href='#\2'>\3</a>"), # internal link
    (re.compile(r"\[url:(.*?)\|(.*?)\]"), r"<a href='\1'>\2</a>"),      # explicit link
    (re.compile(r"\[color:(.*?)\|(.*?)\]"), r"<span style='color: \1;'>\2</span>"), # color override
    (re.compile(r"\[youtube:(\d+)x(\d+)\|(\S+)\]"), r"""<object width="\1" height="\2"><param name="movie" value="http://www.youtube.com/v/$3&amp;hl=en_US&amp;fs=1&amp;color1=0x3a3a3a&amp;color2=0x999999&amp;border=1"><param name="allowFullScreen" value="true"><param name="allowscriptaccess" value="always"><embed type="application/x-shockwave-flash" width="\1" height="\2" src="http://www.youtube.com/v/\3&amp;hl=en_US&amp;fs=1&amp;color1=0x3a3a3a&amp;color2=0x999999&amp;border=1" allowscriptaccess="always" allowfullscreen="true" /></object>"""), # youtube link
    (re.compile(r"""(^|[^:"'>]\b)(\w+:\/\/(?:[^\][ ()'",.]+(?:[\][(),.](?![\][()'",. ]|$)|[[(]?[\])]\.(?![()'",. ]|$))*)+)"""), r"\1<a href='\2'>\2</a>"),    # automatic link with schema
    (re.compile(r"""(^|[^\/:"'>.\w])(www\.(?:[^\][ ()'",.]+(?:[\][(),.](?![\][()'",. ]|$)|[[(]?[\])]\.(?![()'",. ]|$))*)+)"""), r"\1<a href='http://\2'>\2</a>"),    # automatic link http assumed
]
@register.filter
def minifmt(s, _wiki_rules=_wiki_rules):
    lines = s.splitlines()
    for i, line in enumerate(lines):
        line_fmt = line
        for rx, rp in _wiki_rules:
            line_fmt, replaced = rx.subn(rp, line_fmt)
        if line == line_fmt and len(lines) != 1:
            line_fmt = "<p>" + line_fmt + "</p>"
        lines[i] = line_fmt
    fmt = "\n".join(lines)
    return fmt
minifmt.is_safe = True

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
def ppattrs(value, name=None):
    if name:
        return getattr(value, name)
    return set([attr for attr in dir(value) if attr.startswith('pp_')] + 'pp_business pp_charset pp_first_name pp_handling_amount pp_handling_amount pp_invoice pp_last_name pp_item_name pp_mc_currency pp_mc_fee pp_mc_gross pp_notify_version pp_payer_email pp_payer_id pp_payer_status pp_payment_date pp_payment_fee pp_payment_gross pp_payment_status pp_payment_type pp_protection_eligibility pp_quantity pp_receiver_email pp_receiver_id pp_residence_country pp_shipping pp_tax pp_transaction_subject pp_txn_id pp_txn_type pp_verify_sign'.split())
        
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
        template = lambda a: '<a href="%s">%s %s</a>' % (a.get_absolute_url(), a.firstname, a.lastname)
    else:
        template = lambda a: '%s %s' % (a.firstname, a.lastname)
    return set_of(book.authors.all(), template, '(nobody)')
        
@register.simple_tag
def genresof(book, linkify=True):
    if linkify:
        template = lambda g: '<a href="%s">%s</a>' % (g.get_absolute_url(), g.name)
    else:
        template = lambda g: '%s' % (g.name)
    return set_of(book.genres.all(), template, '(none)')
    
@register.simple_tag
def fblike(link):
    return """<iframe id="fbl" src="http://www.facebook.com/plugins/like.php?href=""" + urlquote(link, safe="") + """&amp;layout=button_count&amp;show_faces=true&amp;width=450&amp;action=like&amp;font=trebuchet+ms&amp;colorscheme=light&amp;height=21" scrolling="no" frameborder="0" allowTransparency="true"></iframe>"""
    
@register.simple_tag
def fbrec(link, refkind, ref):
    return """<iframe class="ui-corner-all feature center rightbar" id="fbr" src="http://www.facebook.com/plugins/recommendations.php?site=""" + urlquote(link, safe="") + """&amp;width=155&amp;height=500&amp;header=true&amp;colorscheme=light&amp;font=trebuchet+ms&amp;border_color=%23000&amp;ref=""" + urlquote(refkind, safe="") + "%3A" + urlquote(ref, safe="") + """" scrolling="no" frameborder="0" allowTransparency="true"></iframe>"""

@register.simple_tag
def genre_sidebar():
    t = template.loader.get_template('bookstore/genre_sidebar.html')
    return t.render(Context({'genres': Genre.objects.order_by("display_order")}))

@register.simple_tag
def author_sidebar():
    t = template.loader.get_template('bookstore/author_sidebar.html')
    return t.render(Context({'authors': Person.objects.filter(author=True, visible=True).order_by('-rank')[:6]}))

@register.tag
def bookcard(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, book_variable = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly one arguments" % token.contents.split()[0]
    return FormatBookCardNode(book_variable)
    
class FormatBookCardNode(template.Node):
    def __init__(self, book_variable):
        self.book_reference = template.Variable(book_variable)
    def render(self, context):
        book = self.book_reference.resolve(context)
        t = template.loader.get_template('bookstore/book_summary.html')
        return t.render(Context({'book': book}, autoescape=context.autoescape))