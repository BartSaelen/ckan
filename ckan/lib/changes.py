# encoding: utf-8

'''
Functions used by the helper function compare_pkg_dicts() to analyze
the differences between two versions of a dataset.
'''
from helpers import url_for


def _extras_to_dict(extras_list):
    '''
    Takes a list of dictionaries with the following format:
    [
        {
            "key": <key_0>,
            "value": <value_0>
        },
        ...,
        {
            "key": <key_n>,
            "value": <value_n>
        }
    ]
    and converts it into a single dictionary with the following
    format:
    {
        key_0: value_0,
        ...,
        key_n: value_n

    }
    '''
    ret_dict = {}
    # the extras_list is a list of dictionaries
    for dict in extras_list:
        ret_dict[dict['key']] = dict['value']

    return ret_dict


def _check_resource_changes(change_list, original, new, new_pkg,
                            old_activity_id):
    '''
    Checks whether a dataset's resources have changed - whether new ones have
    been uploaded, existing ones have been deleted, or existing ones have
    been edited. For existing resources, checks whether their names, formats,
    and/or descriptions have changed, as well as whether a new file has been
    uploaded for the resource.
    '''

    # make a set of the resource IDs present in original and new
    original_resource_set = set()
    original_resource_dict = {}
    new_resource_set = set()
    new_resource_dict = {}
    s = u""

    for resource in original['resources']:
        original_resource_set.add(resource['id'])
        original_resource_dict[resource['id']] = {
            u'name': resource['name'],
            u'url': resource['url'],
            u'description': resource['description'],
            u'format': resource['format']}

    for resource in new['resources']:
        new_resource_set.add(resource['id'])
        new_resource_dict[resource['id']] = {
            u'name': resource['name'],
            u'url': resource['url'],
            u'description': resource['description'],
            u'format': resource['format']}

    # get the IDs of the resources that have been added between the versions
    new_resources = list(new_resource_set - original_resource_set)
    for resource_id in new_resources:
        seq2 = (u"<a href=\"", url_for(qualified=True, controller=u"resource",
                action=u"read", id=new['id'], resource_id=resource_id), u"\">",
                new_resource_dict[resource_id]['name'], u"</a>")
        change_list.append(["Added resource",
                            s.join(seq2), u"to",
                            new_pkg])

    # get the IDs of resources that have been deleted between versions
    deleted_resources = list(original_resource_set - new_resource_set)
    for resource_id in deleted_resources:
        seq2 = (u"<a href=\"", url_for(qualified=True, controller=u"resource",
                action=u"read", id=original['id'], resource_id=resource_id) +
                u"?activity_id=" + old_activity_id, u"\">",
                original_resource_dict[resource_id]['name'], u"</a>")
        change_list.append(
            ["Deleted resource", s.join(seq2), u"from", new_pkg])

    # now check the resources that are in both and see if any
    # have been changed
    resources = new_resource_set.intersection(original_resource_set)
    for resource_id in resources:
        original_metadata = original_resource_dict[resource_id]
        new_metadata = new_resource_dict[resource_id]

        if original_metadata['name'] != new_metadata['name']:
            seq2 = (u"<a href=\"", url_for(qualified=True,
                    controller=u"resource",
                    action=u"read",
                    id=original['id'],
                    resource_id=resource_id) +
                    u"?activity_id=" + old_activity_id, u"\">",
                    original_resource_dict[resource_id]['name'], u"</a>")
            seq3 = (u"<a href=\"", url_for(qualified=True,
                    controller=u"resource",
                    action=u"read",
                    id=new['id'],
                    resource_id=resource_id),
                    u"\">",
                    new_resource_dict[resource_id]['name'], u"</a>")
            change_list.append(["Renamed resource", s.join(seq2),
                                u"to", s.join(seq3), u"in", new_pkg])

        # you can't remove a format, but if a resource's format isn't
        # recognized, it won't have one set

        # if a format was not originally set and the user set one
        if not original_metadata['format'] and new_metadata['format']:
            seq2 = (u"<a href=\"", url_for(qualified=True,
                    controller=u"resource",
                    action=u"read",
                    id=new['id'],
                    resource_id=resource_id),
                    u"\">",
                    new_resource_dict[resource_id]['name'], u"</a>")
            seq3 = (u"<a href=\"", url_for(qualified=True,
                    controller=u"organization",
                    action=u"read",
                    id=new['organization']['id']) +
                    u"?res_format=" + new_metadata['format'], u"\">",
                    new_metadata['format'], u"</a>")
            change_list.append([u"Set format of resource", s.join(seq2),
                                u"to", s.join(seq3), u"in", new_pkg])
        # if both versions have a format but the format changed
        elif original_metadata['format'] != new_metadata['format']:
            seq2 = (u"<a href=\"", url_for(qualified=True,
                    controller=u"resource",
                    action=u"read",
                    id=original['id'],
                    resource_id=resource_id)
                    + u"?activity_id=" + old_activity_id, u"\">",
                    original_resource_dict[resource_id]['name'], u"</a>")
            seq3 = (u"<a href=\"", url_for(qualified=True,
                    controller=u"organization",
                    action=u"read",
                    id=new['organization']['id'])
                    + u"?res_format=" + new_metadata['format'], u"\">",
                    new_metadata['format'], u"</a>")
            seq4 = (u"<a href=\"", url_for(qualified=True,
                    controller=u"organization",
                    action=u"read",
                    id=original['organization']['id'])
                    + u"?res_format=" + original_metadata['format'], u"\">",
                    original_metadata['format'], u"</a>")
            change_list.append([u"Set format of resource",
                                s.join(seq2),
                                u"to", s.join(seq3),
                                u"(previously", s.join(seq4) + u")",
                                u"in", new_pkg])

        # if the description changed
        if not original_metadata['description'] and \
                new_metadata['description']:
            seq2 = (u"<a href=\"", url_for(qualified=True,
                    controller=u"resource",
                    action=u"read",
                    id=new['id'],
                    resource_id=resource_id), u"\">",
                    new_resource_dict[resource_id]['name'], u"</a>")
            change_list.append([u"Updated description of resource",
                                s.join(seq2), u"in",
                                new_pkg, u"to <br style=\"line-height:2;\">",
                                u"<blockquote>" + new_metadata['description']
                                + u"</blockquote>"])

        # if there was a description but the user removed it
        elif original_metadata['description'] and \
                not new_metadata['description']:
            seq2 = (u"<a href=\"", url_for(qualified=True,
                    controller=u"resource",
                    action=u"read",
                    id=new['id'],
                    resource_id=resource_id), u"\">",
                    new_resource_dict[resource_id]['name'], u"</a>")
            change_list.append([u"Removed description from resource",
                                s.join(seq2), u"in", new_pkg])

        # if both have descriptions but they are different
        elif original_metadata['description'] != new_metadata['description']:
            seq2 = (u"<a href=\"", url_for(qualified=True,
                    controller=u"resource",
                    action=u"read",
                    id=new['id'],
                    resource_id=resource_id), u"\">",
                    new_resource_dict[resource_id]['name'], u"</a>")
            change_list.append([u"Updated description of resource",
                                s.join(seq2), u"in",
                                new_pkg,
                                u"from <br style=\"line-height:2;\">",
                                u"<blockquote>" +
                                original_metadata['description'] +
                                u"</blockquote>",
                                u"to <br style=\"line-height:2;\">",
                                u"<blockquote>" +
                                new_metadata['description'] +
                                u"</blockquote>"])

        # check if the user uploaded a new file
        # TODO: use regular expressions to determine the actual name of the
        # new and old files
        if original_metadata['url'] != new_metadata['url']:
            seq2 = (u"<a href=\"", url_for(qualified=True,
                    controller=u"resource",
                    action=u"read",
                    id=new['id'],
                    resource_id=resource_id),
                    u"\">",
                    new_resource_dict[resource_id]['name'], u"</a>")
            change_list.append([u"Uploaded a new file to resource",
                                s.join(seq2), u"in", new_pkg])


def _check_metadata_changes(change_list, original, new, new_pkg):
    '''
    Checks whether a dataset's metadata fields (fields in its package
    dictionary not including resources) have changed between two consecutive
    versions and puts a list of formatted summaries of these changes in
    change_list.
    '''
    # if the title has changed
    if original['title'] != new['title']:
        _title_change(change_list, original, new)

    # if the owner organization changed
    if original['owner_org'] != new['owner_org']:
        _org_change(change_list, original, new, new_pkg)

    # if the maintainer of the dataset changed
    if original['maintainer'] != new['maintainer']:
        _maintainer_change(change_list, original, new, new_pkg)

    # if the maintainer email of the dataset changed
    if original['maintainer_email'] != new['maintainer_email']:
        _maintainer_email_change(change_list, original, new, new_pkg)

    # if the author of the dataset changed
    if original['author'] != new['author']:
        _author_change(change_list, original, new, new_pkg)

    # if the author email of the dataset changed
    if original['author_email'] != new['author_email']:
        _author_email_change(change_list, original, new, new_pkg)

    # if the visibility of the dataset changed
    if original['private'] != new['private']:
        change_list.append([u"Set visibility of", new_pkg, u"to",
                            u"Private" if new['private'] else u"Public"])

    # if the description of the dataset changed
    if original['notes'] != new['notes']:
        _description_change(change_list, original, new, new_pkg)

    # make sets out of the tags for each dataset
    original_tags = set([tag['name'] for tag in original['tags']])
    new_tags = set([tag['name'] for tag in new['tags']])
    # if the tags have changed
    if original_tags != new_tags:
        _tag_change(change_list, new_tags, original_tags, new_pkg)

    # if the license has changed
    if original['license_title'] != new['license_title']:
        _license_change(change_list, original, new, new_pkg)

    # if the name of the dataset has changed
    # this is only visible to the user via the dataset's URL,
    # so display the change using that
    if original['name'] != new['name']:
        _name_change(change_list, original, new)

    # if the source URL (metadata value, not the actual URL of the dataset)
    # has changed
    if original['url'] != new['url']:
        _source_url_change(change_list, original, new, new_pkg)

    # if the user-provided version has changed
    if original['version'] != new['version']:
        _version_change(change_list, original, new, new_pkg)

    # check whether fields added by extensions or custom fields
    # (in the "extras" field) have been changed

    _extension_fields(change_list, original, new, new_pkg)
    _extra_fields(change_list, original, new, new_pkg)


def _title_change(change_list, original, new):
    '''
    Appends a summary of a change to a dataset's title between two versions
    (original and new) to change_list.
    '''
    s = u""
    seq2 = (u"<a href=\"", url_for(qualified=True, controller=u"dataset",
            action=u"read", id=new['name']), u"\">",
            new['title'], u"</a>")
    change_list.append([u"Changed title to", s.join(seq2),
                        u"(previously", original['title'] + u")"])


def _org_change(change_list, original, new, new_pkg):
    '''
    Appends a summary of a change to a dataset's organization between
    two versions (original and new) to change_list.
    '''
    s = u""
    seq2 = (u"<a href=\"", url_for(qualified=True,
            controller=u"organization",
            action=u"read",
            id=original['organization']['id']),
            u"\">",
            original['organization']['title'], u"</a>")
    seq3 = (u"<a href=\"", url_for(qualified=True,
            controller=u"organization",
            action=u"read",
            id=new['organization']['id']),
            u"\">",
            new['organization']['title'], u"</a>")
    change_list.append([u"Moved", new_pkg,
                        u"from organization",
                        s.join(seq2),
                        u"to organization",
                        s.join(seq3)])


def _maintainer_change(change_list, original, new, new_pkg):
    '''
    Appends a summary of a change to a dataset's maintainer field between two
    versions (original and new) to change_list.
    '''
    # if the original dataset had a maintainer
    if original['maintainer'] and new['maintainer']:
        change_list.append([u"Set maintainer of", new_pkg,
                            u"to", new['maintainer'],
                            u"(previously", original['maintainer'] + u")"])
    elif not new['maintainer']:
        change_list.append([u"Removed maintainer from", new_pkg])
    else:
        change_list.append([u"Set maintainer of", new_pkg, u"to",
                            new['maintainer']])


def _maintainer_email_change(change_list, original, new, new_pkg):
    '''
    Appends a summary of a change to a dataset's maintainer e-mail address
    field between two versions (original and new) to change_list.
    '''
    s = u""
    seq2 = (u"<a href=\"mailto:", new['maintainer_email'], u"\">",
            new['maintainer_email'], u"</a>")
    # if the original dataset had a maintainer email
    if original['maintainer_email'] and new['maintainer_email']:
        seq3 = (u"<a href=\"mailto:", original['maintainer_email'], u"\">",
                original['maintainer_email'], u"</a>")
        change_list.append([u"Set maintainer e-mail of",
                            new_pkg, u"to", s.join(seq2),
                            u"(previously", s.join(seq3) + u")"])
    elif not new['maintainer_email']:
        change_list.append([u"Removed maintainer e-mail from", new_pkg])
    else:
        change_list.append([u"Set maintainer e-mail of",
                            new_pkg, u"to", s.join(seq2)])


def _author_change(change_list, original, new, new_pkg):
    '''
    Appends a summary of a change to a dataset's author field between two
    versions (original and new) to change_list.
    '''
    # if the original dataset had an author
    if original['author'] and new['author']:
        change_list.append([u"Set author of", new_pkg, u"to", new['author'],
                            u"(previously", original['author'] + u")"])
    elif not new['author']:
        change_list.append([u"Removed author from", new_pkg])
    else:
        change_list.append([u"Set author of", new_pkg, u"to", new['author']])


def _author_email_change(change_list, original, new, new_pkg):
    '''
    Appends a summary of a change to a dataset's author e-mail address field
    between two versions (original and new) to change_list.
    '''
    s = u""
    seq2 = (u"<a href=\"mailto:", new['author_email'], u"\">",
            new['author_email'], u"</a>")
    # if the original dataset had a author email
    if original['author_email'] and new['author_email']:
        seq3 = (u"<a href=\"mailto:", original['author_email'], u"\">",
                original['author_email'], u"</a>")
        change_list.append([u"Set author e-mail of", new_pkg, u"to",
                            s.join(seq2), u"(previously", s.join(seq3) + u")"])
    elif not new['author_email']:
        change_list.append([u"Removed author e-mail from", new_pkg])
    else:
        change_list.append([u"Set author e-mail of", new_pkg,
                            u"to", s.join(seq2)])


def _description_change(change_list, original, new, new_pkg):
    '''
    Appends a summary of a change to a dataset's description between two
    versions (original and new) to change_list.
    '''

    # TODO: find a better way to format the descriptions along with the
    # change summary

    # if the original dataset had a description
    if original['notes'] and new['notes']:
        change_list.append([u"Updated description of", new_pkg,
                            u"from <br style=\"line-height:2;\">",
                            u"<blockquote>" +
                            original['notes'] +
                            u"</blockquote>",
                            u"to <br style=\"line-height:2;\">",
                            u"<blockquote>" +
                            new['notes'] +
                            u"</blockquote>"])
    elif not new['notes']:
        change_list.append([u"Removed description from", new_pkg])
    else:
        change_list.append([u"Updated description of", new_pkg,
                            u"to <br style=\"line-height:2;\">",
                            u"<blockquote>" +
                            new['notes'] +
                            u"</blockquote>"])


def _tag_change(change_list, new_tags, original_tags, new_pkg):
    '''
    Appends a summary of a change to a dataset's tag list between two
    versions (original and new) to change_list.
    '''
    s = u""
    deleted_tags = original_tags - new_tags
    deleted_tags_list = list(deleted_tags)
    if len(deleted_tags) == 1:
        seq2 = (u"<a href=\"", url_for(qualified=True,
                controller=u"dataset",
                action=u"search",
                id=deleted_tags_list[0]),
                u"\">",
                deleted_tags_list[0], u"</a>")
        change_list.append([u"Removed tag", s.join(seq2), u"from", new_pkg])
    elif len(deleted_tags) > 1:
        seq2 = [
            u"<li><a href=\"" +
            url_for(
                qualified=True,
                controller=u"dataset",
                action=u"search",
                id=deleted_tags_list[i]
            ) +
            u"\">" + deleted_tags_list[i] + u"</a></li> "
            for i in range(0, len(deleted_tags))
        ]
        change_list.append([u"Removed the following tags from", new_pkg,
                            u"<ul>", s.join(seq2), u"</ul>"])

    added_tags = new_tags - original_tags
    added_tags_list = list(added_tags)
    if len(added_tags) == 1:
        seq2 = (u"<a href=\"", url_for(qualified=True,
                controller=u"dataset",
                action=u"search",
                id=added_tags_list[0]),
                u"\">",
                added_tags_list[0], u"</a>")
        change_list.append([u"Added tag", s.join(seq2), u"to", new_pkg])
    elif len(added_tags) > 1:
        seq2 = [u"<li><a href=\"" + url_for(qualified=True,
                controller=u"dataset",
                action=u"search",
                id=added_tags_list[i]) +
                u"\">" + added_tags_list[i] + u"</a></li> "
                for i in range(0, len(added_tags))]
        change_list.append([u"Added the following tags to", new_pkg,
                            u"<ul>", s.join(seq2), u"</ul>"])


def _license_change(change_list, original, new, new_pkg):
    '''
    Appends a summary of a change to a dataset's license between two versions
    (original and new) to change_list.
    '''
    s = u""
    seq2 = ()
    seq3 = ()
    # if the license has a URL, use it
    if u'license_url' in original and original['license_url']:
        seq2 = (u"<a href=\"", original['license_url'], u"\">",
                original['license_title'], u"</a>")
    else:
        seq2 = (original['license_title'])
    if u'license_url' in new and new['license_url']:
        seq3 = (u"<a href=\"", new['license_url'], u"\">",
                new['license_title'], u"</a>")
    else:
        seq3 = (new['license_title'])
    change_list.append([u"Changed the license of", new_pkg, u"to",
                        s.join(seq3), u"(previously", s.join(seq2) + u")"])


def _name_change(change_list, original, new):
    '''
    Appends a summary of a change to a dataset's name (and thus the URL it
    can be accessed at) between two versions (original and new) to
    change_list.
    '''
    s = u""
    old_url = url_for(
        qualified=True,
        controller=u"dataset",
        action=u"read",
        id=original['name']
    )
    new_url = url_for(
        qualified=True,
        controller=u"dataset",
        action=u"read",
        id=new['name']
    )
    seq2 = (u"<a href=\"", old_url, u"\">", old_url, u"</a>")
    seq3 = (u"<a href=\"", new_url, u"\">", new_url, u"</a>")
    change_list.append([u"Moved the dataset from", s.join(seq2),
                        u"to", s.join(seq3)])


def _source_url_change(change_list, original, new, new_pkg):
    '''
    Appends a summary of a change to a dataset's source URL (metadata field,
    not its actual URL in the datahub) between two versions (original and
    new) to change_list.
    '''
    s = u""
    seq2 = (u"<a href=\"", original['url'], u"\">", original['url'], u"</a>")
    seq3 = (u"<a href=\"", new['url'], u"\">", new['url'], u"</a>")
    if original['url'] and new['url']:
        change_list.append([u"Changed the source URL of", new_pkg,
                            u"from", s.join(seq2), u"to", s.join(seq3)])
    elif not new['url']:
        change_list.append([u"Removed source URL from", new_pkg])
    else:
        change_list.append([u"Changed the source URL of",
                            new_pkg, u"to", s.join(seq3)])


def _version_change(change_list, original, new, new_pkg):
    '''
    Appends a summary of a change to a dataset's version field (inputted
    by the user, not from version control) between two versions (original
    and new) to change_list.
    '''
    if original['version'] and new['url']:
        change_list.append([u"Changed the version of", new_pkg,
                            u"from", original['version'],
                            u"to", new['version']])
    elif not new['url']:
        change_list.append([u"Removed version number from", new_pkg])
    else:
        change_list.append([u"Changed the version of", new_pkg,
                            u"to", new['version']])


def _extension_fields(change_list, original, new, new_pkg):
    '''
    Checks whether any fields that have been added to the package
    dictionaries by CKAN extensions have been changed between versions.
    If there have been any changes between the two versions (original and
    new), a general summary of the change is appended to change_list. This
    function does not produce summaries for fields added or deleted by
    extensions, since these changes are not triggered by the user in the web
    interface or API.
    '''
    # list of the default metadata fields for a dataset
    # any fields that are not part of this list are custom fields added by a
    # user or extension
    fields = [
        u'owner_org', u'maintainer', u'maintainer_email',
        u'relationships_as_object', u'private', u'num_tags',
        u'id', u'metadata_created', u'metadata_modified',
        u'author', u'author_email', u'state', u'version',
        u'license_id', u'type', u'resources', u'num_resources',
        u'tags', u'title', u'groups', u'creator_user_id',
        u'relationships_as_subject', u'name', u'isopen', u'url',
        u'notes', u'license_title', u'extras',
        u'license_url', u'organization', u'revision_id'
    ]
    fields_set = set(fields)

    # if there are any fields from extensions that are in the new dataset and
    # have been updated, print a generic message stating that
    original_set = set(original.keys())
    new_set = set(new.keys())

    # set of additional fields in the new dictionary
    addl_fields_new = new_set - fields_set
    # set of additional fields in the original dictionary
    addl_fields_original = original_set - fields_set
    # set of additional fields in both
    addl_fields = addl_fields_new.intersection(addl_fields_original)

    # do NOT display a change if any additional fields have been
    # added or deleted, since that is not a change made by the user
    # from the web interface

    # if additional fields have been changed
    addl_fields_list = list(addl_fields)
    for field in addl_fields_list:
        if original[field] != new[field]:
            if original[field]:
                change_list.append([u"Changed value of field",
                                    field.capitalize(), u"to",
                                    new[field], u"(previously",
                                    original[field] + u")", u"in", new_pkg])
            else:
                change_list.append([u"Changed value of field",
                                    field.capitalize(), u"to",
                                    new[field], u"in", new_pkg])


def _extra_fields(change_list, original, new, new_pkg):
    '''
    Checks whether a user has added, removed, or changed any custom fields
    from the web interface (or API?) and appends a summary of each change to
    change_list.
    '''

    s = u""
    if u'extras' in new:
        extra_fields_new = _extras_to_dict(new['extras'])
        extra_new_set = set(extra_fields_new.keys())

        # if the original version has an extra fields, we need
        # to compare the new version'sextras to the original ones
        if u'extras' in original:
            extra_fields_original = _extras_to_dict(original['extras'])
            extra_original_set = set(extra_fields_original.keys())

            # if some fields were added
            new_fields = list(extra_new_set - extra_original_set)
            if len(new_fields) == 1:
                if extra_fields_new[new_fields[0]]:
                    change_list.append(
                        [u"Added field",
                        s.join((u"<q>",
                                new_fields[0],
                                u"</q>")),
                        u"with value",
                        s.join((u"<q>",
                                extra_fields_new[new_fields[0]],
                                u"</q>")),
                        u"to", new_pkg]
                    )
                else:
                    change_list.append(
                        [u"Added field",
                        s.join((u"<q>",
                                new_fields[0],
                                u"</q>")
                            ),
                        u"to", new_pkg]
                    )
            elif len(new_fields) > 1:
                seq2 = [u"<li><q>" + new_fields[i] + u"</q> with value <q>" +
                        extra_fields_new[new_fields[i]] + u"</q></li>"
                        if extra_fields_new[new_fields[i]]
                        else u"<li><q>" + new_fields[i] + u"</q></li>"
                        for i in range(0, len(new_fields))]
                change_list.append([u"Added the following fields to",
                                    new_pkg, u"<ul>", s.join(seq2), u"</ul>"])

            # if some fields were deleted
            deleted_fields = list(extra_original_set - extra_new_set)
            if len(deleted_fields) == 1:
                change_list.append([u"Removed field", s.join((u"<q>",
                                    deleted_fields[0], u"</q>")),
                                    u"from", new_pkg])
            elif len(deleted_fields) > 1:
                seq2 = [u"<li><q>" + deleted_fields[i] + u"</q></li>"
                        for i in range(0, len(deleted_fields))]
                change_list.append([u"Removed the following fields from",
                                    new_pkg, u"<ul>", s.join(seq2), u"</ul>"])

            # if some existing fields were changed
            # list of extra fields in both the original and new versions
            extra_fields = list(extra_new_set.intersection(extra_original_set))
            for field in extra_fields:
                if extra_fields_original[field] != extra_fields_new[field]:
                    if extra_fields_original[field]:
                        change_list.append(
                            [u"Changed value of field",
                            s.join((u"<q>",
                                    field, u"</q>")),
                            u"to",
                            s.join((u"<q>",
                                    extra_fields_new[field],
                                    u"</q>")),
                            u"(previously",
                            s.join((u"<q>",
                                    extra_fields_original[field],
                                    u"</q>")) +
                            u")", u"in", new_pkg]
                        )
                    else:
                        change_list.append(
                            [u"Changed value of field",
                            s.join((u"<q>", field, u"</q>")),
                            u"to",
                            s.join((u"<q>",
                                    extra_fields_new[field],
                                    u"</q>")),
                            u"in", new_pkg]
                        )

        # if the original version didn't have an extras field,
        # the user could only have added a field (not changed or deleted)
        else:
            new_fields = list(extra_new_set)
            if len(new_fields) == 1:
                if extra_fields_new[new_fields[0]]:
                    change_list.append(
                        [u"Added field",
                        s.join((u"<q>", new_fields[0], u"</q>")),
                        u"with value",
                        s.join((u"<q>",
                                extra_fields_new[new_fields[0]],
                                u"</q>")),
                        u"to", new_pkg]
                    )
                else:
                    change_list.append([u"Added field",
                                        s.join((u"<q>",
                                                new_fields[0],
                                                u"</q>")),
                                        u"to", new_pkg])
            elif len(new_fields) > 1:
                seq2 = [u"<li><q>" + new_fields[i] + u"</q> with value <q>" +
                        extra_fields_new[new_fields[i]] + u"</q></li>"
                        if extra_fields_new[new_fields[i]]
                        else u"<li><q>" + new_fields[i] + u"</q></li>"
                        for i in range(0, len(new_fields))]
                change_list.append([u"Added the following fields to",
                                    new_pkg, u"<ul>", s.join(seq2), u"</ul>"])

    elif u'extras' in original:
        deleted_fields = _extras_to_dict(original['extras']).keys()
        if len(deleted_fields) == 1:
            change_list.append([u"Removed field", s.join((u"<q>",
                                deleted_fields[0], u"</q>")), u"from",
                                new_pkg])
        elif len(deleted_fields) > 1:
            seq2 = [u"<li><q>" + deleted_fields[i] +
                    u"</q></li>" for i in range(0, len(deleted_fields))]
            change_list.append([u"Removed the following fields from",
                                new_pkg, u"<ul>", s.join(seq2), u"</ul>"])