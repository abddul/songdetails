"""
:mod:`songdetails.scanners`
===========================
"""
import songdetails

# Pylint disable settings --------------------
#
# ToDos, DocStrings:
# pylint: disable-msg=W0511,W0105 
#
# Protected member access: 
# pylint: disable-msg=W0212
#
# Too many instance attributes, Too few public methods, Too many init arguments:
# pylint: disable-msg=R0902,R0903,R0913

_SCANNERS = []
"""Scanners registered."""

_MULTI_SCANNERS = []
"""Multi scanners registered."""

_HAS_DEFAULTS = False

def register_file_scan(scan_function, extension_matches=None, 
                       custom_matcher=None):
    """Register single file scanner.
    
    :param scan_function: Scan function returning SongDetails.
    :param extension_matches: Match files by extension, for example 
        ``("mp3", "mp2", "mp1")``.
    :param custom_matcher: Match files by custom function.
    
    """
    def extension_matcher(filepath):
        """Match by given extensions"""
        for ext in extension_matches:
            if filepath.endswith(ext):
                return True
        return False
    
    file_path_matcher = custom_matcher or extension_matcher
    _SCANNERS.append((scan_function, file_path_matcher))


def register_multifile_scan(scan_files_function, files_matcher):
    """Register multi file scanner.
    
    :param scan_files_function: Scan function returning SongDetails from list of 
        files.
    :param files_matcher: Function returning True for list of files that match
        or False for files that doesn't match.
        
    """
    _MULTI_SCANNERS.append((scan_files_function, files_matcher))


def scan_files(files):
    """Scan several files for SongDetails.
    
    :param files: List of files to be scanned, you can also give this single 
        file.
    :type files: [string, ...]
    
    :rtype: [:mod:`SongDetails`, ...]
    :return: List of SongDetails found, list maybe empty if nothing is found.
    
    """
    
    # If the given files are not iterable, such as string. Make it iterable.
    if not hasattr(files, "__iter__"):
        files = [files]
    
    # Register default scanners
    _register_default_scanners()
    
    # Search from all m
    songs = []
    for scan_files_, files_matcher in _MULTI_SCANNERS:
        if files_matcher(files):
            songs.append(scan_files_(files))
            
    for file_path in files:
        song = scan(file_path)
        if song is not None:
            songs.append(song)
            
    return songs


def scan(file_path):
    """Scan single file
    
    :param file_path: Path to the file.
    
    :return: Returns the SongDetails matching the given file path.
    :rtype: SongDetails or None
    
    """
    
    _register_default_scanners()
    
    for scan_function, file_path_matcher in _SCANNERS:
        if file_path_matcher(file_path):
            song = scan_function(file_path)
            if song is not None:
                return song
    return None


def _register_default_scanners():
    """Registers the default scanners provided."""
    from mp3details.scanners import scan as mp3_scan
    if _HAS_DEFAULTS:
        return
    songdetails.scanners._HAS_DEFAULTS = True
    register_file_scan(mp3_scan, ('.mp3', ))