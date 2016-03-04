# Copyright 2012 VPAC, http://www.vpac.org
# Copyright 2013-2016 Marcus Furlong <furlongm@gmail.com>
#
# This file is part of Patchman.
#
# Patchman is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 only.
#
# Patchman is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Patchman. If not, see <http://www.gnu.org/licenses/>

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q

from rest_framework import viewsets

from patchman.util.filterspecs import Filter, FilterBar
from patchman.packages.models import PackageName, Package, PackageUpdate
from patchman.arch.models import PackageArchitecture
from patchman.packages.serializers import PackageNameSerializer, PackageSerializer, \
        PackageUpdateSerializer


@login_required
def package_list(request):

    packages = PackageName.objects.select_related()

    if 'arch' in request.GET:
        packages = packages.filter(
            package__arch=int(request.GET['arch'])).distinct()

    if 'packagetype' in request.GET:
        packages = packages.filter(
            package__packagetype=request.GET['packagetype']).distinct()

    if 'search' in request.GET:
        terms = request.GET['search'].lower()
        query = Q()
        for term in terms.split(' '):
            q = Q(name__icontains=term)
            query = query & q
        packages = packages.filter(query)
    else:
        terms = ''

    try:
        page_no = int(request.GET.get('page', 1))
    except ValueError:
        page_no = 1

    p = Paginator(packages, 50)

    try:
        page = p.page(page_no)
    except (EmptyPage, InvalidPage):
        page = p.page(p.num_pages)

    filter_list = []
    filter_list.append(
        Filter(request, 'arch', PackageArchitecture.objects.all()))
#   Disabled due to being a huge slowdown
#    filter_list.append(
#        Filter(
#            request, 'packagetype',
#            Package.objects.values_list('packagetype', flat=True).distinct()))
    filter_bar = FilterBar(request, filter_list)

    return render(request,
                  'packages/package_list.html',
                  {'page': page,
                   'filter_bar': filter_bar,
                   'terms': terms}, )


@login_required
def package_detail(request, packagename):

    package = get_object_or_404(PackageName, name=packagename)
    allversions = Package.objects.select_related().filter(name=package.id)

    return render(request,
                  'packages/package_detail.html',
                  {'package': package,
                   'allversions': allversions}, )


#@login_required
class PackageNameViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows package names to be viewed or edited.
    """
    queryset = PackageName.objects.all()
    serializer_class = PackageNameSerializer


#@login_required
class PackageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows packages to be viewed or edited.
    """
    queryset = Package.objects.all()
    serializer_class = PackageSerializer


#@login_required
class PackageUpdateViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows packages updates to be viewed or edited.
    """
    queryset = PackageUpdate.objects.all()
    serializer_class = PackageUpdateSerializer
