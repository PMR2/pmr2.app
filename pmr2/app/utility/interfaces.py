import zope.interface


class ILatestRelatedExposureTool(zope.interface.Interface):
    """
    A tool for finding latest exposures from a given supported context
    object.
    """

    def related_to_context(context):
        """
        Returns a mapping (OrderedDict) of exposures related to the
        provided context, ordered by modification date in reverse order,
        in the following form:

        "/portal/path/to/workspace": {
            "this": boolean,  # true if the workspace related to context
            "workspace": {
                "commit_id": str,
                "title": str,
                "uri": str,
            },
            "exposure": {
                "modified": DateTime,
                "title": str,
                "uri": str,
            }
        }
        """
