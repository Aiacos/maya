"""ReferencesAction is the operations done when saving to import namespaces. """

import maya.cmds as mc

from arise.utils.decorators_utils import simple_catch_error_dec

class ReferencesAction(object):
    """ReferenceAction is the operations done when saving to import namespaces. """
    def __init__(self):
        self.name = "Import References"
        self.info = "Import any references in scene on export"
        self.position = 100
        self.is_checked = True
        self.post_action = False

    @staticmethod
    @simple_catch_error_dec
    def run_action(_):
        """Run import references operation. """
        print("\n#########################################################")
        print("########## Action: 'Import References' START. ###########")
        print("#########################################################\n")

        for ref_path in mc.file(q=True, reference=True):
            namespace = mc.referenceQuery(ref_path, namespace=True, shortName=True)
            mc.file(ref_path, importReference=True)
            mc.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)

        return "Action successful"
