# $Id$

import os, re
import glob
from cgi import escape

LIB_NAMES = (
    'generic_lib', 'content_lib', 'header_lib', # CPSDefault
    'error_lib',
    # 'box_lib',
    'layout_lib',                       # CPSDocument
    'forum_comment_lib',                # CPSForum
    'subscriptions_lib',                # CPSSubscriptions
    'navigation_lib', 'catalognavigation_lib' # CPSNavigation
)

macro_define_pattern = re.compile(
    r"(\<metal\:block\s+define\-macro=\"(\w+)\")")
macro_use_pattern_str = r"use\-macro\=\"here\/(?P<lib_name>(%s))\/macros\/(?P<macro_name>\w+)\""
EOM_PATTERN = r"</metal:block>"

MACRO_NEW_HEADER = """<!-- a %s macro -->
<!-- $Id$ -->

"""

def clear_comment(comment):
    # remove html tags and return an html comments
    return "<!--\n%s\n-->\n\n" % escape(comment.strip())

def split_macro_lib(file_path):
    # split foo_lib file into foo_lib_(macro_name).pt files
    print "### split macro lib file: %s" % file_path
    file_created_count = 0

    if not os.path.exists(file_path):
        print "###    file not found"
        return file_created_count

    f = open(file_path, 'r')
    content = f.read()
    f.close()

    dir_path = os.path.dirname(file_path)
    lib_file = os.path.basename(file_path)
    lib_name = os.path.splitext(lib_file)[0]

    # split <metal:block define-macro
    splitted = macro_define_pattern.split(content)
    comment = clear_comment(splitted[0])
    macro_count = 0
    for i in range(1, len(splitted), 3):
        macro_count += 1
        macro_start, macro_name, macro_end = splitted[i:i+3]
        # end of macro_end contain next comment
        end_idx = macro_end.rfind(EOM_PATTERN)
        if end_idx >= 0:
            end_idx += len(EOM_PATTERN)
            next_comment = clear_comment(macro_end[end_idx:])
            macro_end = macro_end[:end_idx]
        else:
            next_comment = ''
        macro = [MACRO_NEW_HEADER % lib_name, comment,
                 macro_start, macro_end]
        macro = ''.join(macro)
        comment = next_comment

        # save macro into a new file
        new_file_name = '%s_%s.pt' % (lib_name, macro_name)
        new_file_path = os.path.join(dir_path, new_file_name)
        if not os.path.exists(new_file_path):
            print "###    create %s" % new_file_path
            f = open(new_file_path, "w")
            f.write(macro)
            file_created_count += 1
    print "###    found %s macros, generate %s files" % (
        macro_count, file_created_count)
    return file_created_count

def rename_macro_lib(file_path):
    # rename a foo_lib.pt into foo_lib.pt.before_split_macro_lib
    path, ext = os.path.splitext(file_path)
    if ext != '.pt':
        print "### can not rename macro %s file_path"
        return
    new_file_path = '%s.before_splitting' % file_path
    if os.path.exists(new_file_path):
        os.remove(new_file_path)
    rename(file_path, new_file_path)
    print "###   rename macro_lib into %s" new_file_path


def replace_use_macro_lib(file_path, lib_names):
    # replace use-macro="here/foo_lib/macros/bar"
    # by use-macro="here/foo_lib_bar/macros/bar"
    # if foo_lib is in lib_names
    pattern_str = macro_use_pattern_str % '|'.join(lib_names)
    macro_use_pattern = re.compile(pattern_str)
    content = open(file_path, 'r').read()
    content_len = len(content)
    content = macro_use_pattern.sub(r'use-macro="here/\g<lib_name>_\g<macro_name>/macros/\g<macro_name>', content)
    new_content_len = len(content)
    if new_content_len != content_len:
        print "### Changing use-macro in zpt %s" % file_path
    return


def find_macro_lib_paths(lib_names):
    # return all lib_paths
    lib_paths = []
    for lib_name in lib_names:
        lib_paths.extend(glob.glob('Products/*/skins/*/%s.pt' % lib_name))

    return lib_paths

def find_zpt():
    # return all zpt that may contains macro_lib reference
    zpts = glob.glob('Products/*/skins/*/*.pt')
    for product in ('CMF', 'BtreeFolder', 'DCWorkflow', 'Localizer'
                    'OpenPTi18n', 'TranslationService', 'VerboseSecurity',
                    'WingDBG', 'DocFinderEverywhere', 'Epoz'):
        zpts = [x for x in zpts if x.find(product) == -1]
    return zpts

def split_all_macro_libs(lib_names):
    libs = find_macro_lib_paths(lib_names)
    new_file_count = 0
    for lib in libs:
        ret = split_macro_lib(lib)
        if ret:
            new_file_count += ret
            rename_macro_lib(lib)
    print "### total macro file created: %s" % new_file_count

def replace_all_use_macro_lib(lib_names):
    zpts = find_zpt()
    for zpt in zpts:
        replace_use_macro_lib(zpt, lib_names)



