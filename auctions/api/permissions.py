from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsListingOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission for listings - only allow listing owners to edit/delete.
    Anyone can view active listings.
    """

    def has_permission(self, request, view):
        # Allow read access to anyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations, user must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the listing
        return obj.user == request.user


class IsCommentOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission for comments - only allow comment authors to edit/delete.
    """

    def has_permission(self, request, view):
        # Allow read access to anyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations, user must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the comment
        return obj.user == request.user


class IsBidOwnerOrListingOwner(permissions.BasePermission):
    """
    Custom permission for bids - only allow bid owners and listing owners to view.
    """

    def has_permission(self, request, view):
        # User must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow access to bid owner or listing owner
        return obj.user == request.user or obj.listing.user == request.user


class IsWatchlistOwner(permissions.BasePermission):
    """
    Custom permission for watchlist - only allow watchlist owners to access.
    """

    def has_permission(self, request, view):
        # User must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Only allow access to watchlist owner
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff
