# This code checks to see if this module is being run directly. 
# If so, it registers the top level directory of SLA so that 
# sibling modules can be used.
if __name__ == '__main__':
    from sys import path
    from os.path import dirname
    localdir = dirname(path[0]).rpartition('\\')[0]
    # Example: 'e:\Python\state_law_analysis'
    if localdir not in path:
        path.append(localdir)

from state_law_analysis.Utility.string import StrUtil

