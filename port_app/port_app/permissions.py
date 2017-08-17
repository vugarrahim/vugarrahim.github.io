from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import View


class MultiplePermissionsMixin(View):
    permissions = None
    redirect_url = None

    def get_permissions(self):
        # if not isinstance(self.permissions, dict):
        #     raise ValueError
        # else:
        #     if not(self.permissions.get('all', None) and self.permissions.get('any', None)):
        #         raise ValueError
        return self.permissions

    def get_all_perms_result(self, request):
        permissions = self.get_permissions()
        all_perms = permissions.get('all') or None
        all_perms_result = [request.user.has_perm(perm) for perm in all_perms]
        return all(all_perms_result)

    def get_any_perms_result(self, request):
        permissions = self.get_permissions()
        any_perms = permissions.get("any") or None
        any_perms_result = [request.user.has_perm(perm) for perm in any_perms]
        return any(any_perms_result)

    def has_permissions(self, request):
        permissions = self.get_permissions()
        if permissions.get('all', None) and permissions.get('any', None):
            return all((self.get_all_perms_result(request), self.get_any_perms_result(request)))
        elif permissions.get('all', None):
            return self.get_all_perms_result(request)
        elif permissions.get('any', None):
            return self.get_any_perms_result(request)

    def dispatch(self, request, *args, **kwargs):
        if self.has_permissions(request):
            return super(MultiplePermissionsMixin, self).dispatch(request, *args, **kwargs)
        else:
            if self.redirect_url:
                return redirect(self.redirect_url)
            else:
                raise Http404
