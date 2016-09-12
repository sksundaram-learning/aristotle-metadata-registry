from channels.routing import route, route_class, include
from haystack_channels.routing import channel_routing as haystack_routing

channel_routing = [
    route("aristotle_mdr.channels.concept_changes.concept_saved", "aristotle_mdr.channels.concept_changes.concept_saved"),
    route("aristotle_mdr.channels.concept_changes.new_comment_created", "aristotle_mdr.channels.concept_changes.new_comment_created"),
    route("aristotle_mdr.channels.concept_changes.new_post_created", "aristotle_mdr.channels.concept_changes.new_post_created"),
    route("aristotle_mdr.things", "aristotle_mdr.channels.consumers.thing_consumer"),
    route_class("aristotle_mdr.channels.consumers.ConceptConsumer", path=r"^aristotle_mdr.concepts"),
    include(haystack_routing)
]
