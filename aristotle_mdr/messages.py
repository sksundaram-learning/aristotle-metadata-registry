from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from notifications import notify
from aristotle_mdr.utils import url_slugify_concept, url_slugify_workgroup

def favourite_updated(recipient,obj):
    notify.send(obj, recipient=recipient, verb="changed a favourited item",
                description=_('A favourite item <a href="%(obj_url)s">(%(item)s)</a> has been changed.') %
                    {'item': obj, 'obj_url':url_slugify_concept(obj)})

def workgroup_item_updated(recipient,obj):
    notify.send(obj, recipient=recipient, verb="modified item in workgroup", target=obj.workgroup,
                description=_('An item <a href="%(obj_url)s">(%(item)s)</a> has been updated in the workgroup "%(workgroup)s"') %
                    {'item':obj, 'obj_url':url_slugify_concept(obj), 'workgroup': obj.workgroup})

def workgroup_item_new(recipient,obj):
    notify.send(obj, recipient=recipient, verb="new item in workgroup", target=obj.workgroup,
                description=_('An new item <a href="%(obj_url)s">(%(item)s)</a> is in the workgroup "%(workgroup)s"') %
                    {'item':obj, 'obj_url':url_slugify_concept(obj), 'workgroup': obj.workgroup})


def new_comment_created(comment):
    post = comment.post
    author_name = comment.author.get_full_name() or comment.author
    notify.send(comment.author, recipient=post.author, verb="comment on post", target=post,
                description=_('%(commenter)s commented on <a href="%(post_url)s">%(post)s</a>') %
                    {'commenter':author_name, 'post':post.title, 'post_url':reverse("aristotle:discussionsPost",args=[post.id])})

def new_post_created(post,recipient):
    op_name = post.author.get_full_name() or post.author
    notify.send(post.author, recipient=recipient, verb="made a post", target=post.workgroup,
                description=_('%(op)s made a new post <a href="%(post_url)s">"%(post)s"</a> in the workgroup "%(workgroup)s" ')
                % {'op':op_name, 'post':post.title, 'workgroup':post.workgroup, 'post_url':reverse("aristotle:discussionsPost",args=[post.id])})
