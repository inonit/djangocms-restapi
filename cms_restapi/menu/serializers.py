# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField


class NodeAttributeSerializer(serializers.Serializer):
    """
    Serializes ``NavigationNode.attr``
    """
    auth_required = serializers.BooleanField()
    is_home = serializers.BooleanField()
    redirect_url = serializers.CharField()
    reverse_id = serializers.IntegerField()
    soft_root = serializers.BooleanField()
    visible_for_anonymous = serializers.BooleanField()
    visible_for_authenticated = serializers.BooleanField()


class NavigationNodeSerializer(serializers.Serializer):
    """
    Serializes a ``NavigationNode``
    """
    id = serializers.IntegerField()
    title = serializers.CharField()
    url = serializers.CharField()
    namespace = serializers.CharField()
    visible = serializers.BooleanField()
    ancestor = serializers.BooleanField()
    descendant = serializers.BooleanField()
    sibling = serializers.BooleanField()
    is_leaf_node = serializers.BooleanField()
    level = serializers.IntegerField()
    menu_level = serializers.IntegerField()
    parent_id = serializers.IntegerField()
    parent_namespace = serializers.CharField()
    attributes = serializers.SerializerMethodField()
    children = serializers.ListField(child=RecursiveField())

    def get_attributes(self, instance):
        return NodeAttributeSerializer(instance.attr, many=False).data
