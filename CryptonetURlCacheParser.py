# This is a parser for the certutil cache files
#
# The following is the structure of the cache files:
# 12 bytes unknown
# 4 bytes (uint32) urlSize
# 8 bytes (uint64) FILETIME
# 64 bytes unknown
# 8 bytes (uint64) FILETIME
# 4 bytes unknown
# 4 bytes (uint32) etag size
# 8 bytes unknown
# 4 bytes (uint32) file size
# urlSize utf-16-le URL string
# etag utf-16-le hash string (Sometimes)
# =========================================
# For more details refere to my blog post : https://u0041.co/blog/post/3


import struct
import os
from datetime import datetime, timedelta
import hashlib


__author__ = "AbdulRhman Alfaifi"
__version__ = "1.2"
__maintainer__ = "AbdulRhman Alfaifi"
__license__ = "GPL"
__status__ = "Development"


class CertutilCacheParser:
    def __init__(self, filePath):
        self.filePath = filePath
        if not os.path.isfile(self.filePath):
            raise FileNotFoundError(f"The cache file '{self.filePath}' not found.")

    # https://stackoverflow.com/questions/2150739/iso-time-iso-8601-in-python
    def FILETIMEToISO(self, ft):
        us = (ft - 116444736000000000) // 10
        dtObj = datetime(1970, 1, 1) + timedelta(microseconds=us)
        return dtObj.isoformat()

    def MD5(self, fname):
        if not os.path.exists(fname):
            return "N/A"
        try:
            hash_md5 = hashlib.md5()
            with open(fname, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest().upper()
        except:
            return "ERROR"

    def Parse(self, useContent=True):
        try:
            with open(self.filePath, "rb") as cacheFile:
                data = cacheFile.read(116)
                if len(data) != 116:
                    return None
                header = struct.unpack("<12xIQ64xQ4xI8xI", data)
                urlSize = header[0]
                last_download_time = self.FILETIMEToISO(header[1])
                last_modification_time_header = self.FILETIMEToISO(header[2])
                etagsize = header[3]
                fileSize = header[4]
                # url
                url_bytes = cacheFile.read(urlSize)
                if len(url_bytes) != urlSize:
                    return None
                try:
                    url = url_bytes.decode("utf-16-le")[:-1]
                except:
                    return None
                # etag
                etag_bytes = cacheFile.read(etagsize)
                if len(etag_bytes) != etagsize:
                    return None
                try:
                    etag = etag_bytes.decode("utf-16-le").replace('"', "")[:-1]
                except:
                    etag = "Not Found"

                parsedData = {
                    "LastDownloadTime": last_download_time,
                    "LastModificationTimeHeader": last_modification_time_header,
                    "URL": url,
                    "FileSize": fileSize,
                    "ETag": etag,
                    "FullPath": self.filePath,
                }
                if useContent:
                    contentFilePath = os.path.normpath(os.path.join(os.path.dirname(self.filePath), "..", "Content", os.path.basename(self.filePath)))
                    md5 = self.MD5(contentFilePath)
                    parsedData["MD5"] = md5
                return parsedData
        except:
            return None


if __name__ == "__main__":
    import glob
    import argparse
    import sys
    import json
    import csv

    certutilCachePaths = [
        "C:\\Windows\\System32\\config\\systemprofile\\AppData\\LocalLow\\Microsoft\\CryptnetUrlCache\\Metadata",
        "C:\\Windows\\SysWOW64\\config\\systemprofile\\AppData\\LocalLow\\Microsoft\\CryptnetUrlCache\\Metadata",
    ] + glob.glob(
        "C:\\Users\\*\\AppData\\LocalLow\\Microsoft\\CryptnetUrlCache\\MetaData"
    )

    parser = argparse.ArgumentParser(
        description="CryptnetUrlCache Metadata Parser - Developded by AbdulRhman Alfaifi"
    )
    parser.add_argument(
        "-d",
        "--dirs",
        nargs="+",
        help="A list of dirs that contain certutil cache files (default: all certutil cache paths)",
        default=certutilCachePaths,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="The file path to write the output to (default: stdout)",
        default=sys.stdout,
    )
    parser.add_argument(
        "--outputFormat",
        help="The output formate (default: csv)",
        default="csv",
        choices=["csv", "json", "jsonl"],
    )
    parser.add_argument(
        "--useContent",
        action="store_true",
        help="Try finding the cached file and calculate the MD5 hash for it",
        default=False,
    )
    parser.add_argument(
        "--noHeaders",
        action="store_true",
        help="Don't print headers when using CSV as the output format",
        default=False,
    )

    args = parser.parse_args()

    if args.outputFormat == "csv":
        if isinstance(args.output, str):
            f = open(args.output, "w")
            results = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC, lineterminator="\n")
        else:
            results = csv.writer(
                args.output, quoting=csv.QUOTE_NONNUMERIC, lineterminator="\n"
            )
        if args.useContent and not args.noHeaders:
            results.writerow(
                ["LastDownloadTime", "LastModificationTimeHeader", "URL", "FileSize", "ETag", "FullPath", "MD5"]
            )
        elif not args.noHeaders:
            results.writerow(
                ["LastDownloadTime", "LastModificationTimeHeader", "URL", "FileSize", "ETag", "FullPath"]
            )
    elif args.outputFormat == "json":
        results = []
    else:
        if isinstance(args.output, str):
            results = open(args.output, "w")
        else:
            results = args.output

    for path in args.dirs:
        for root, dirs, files in os.walk(path):
            for file in files:
                fullPath = os.path.join(root, file)
                res = CertutilCacheParser(fullPath).Parse(useContent=args.useContent)
                if res:
                    if args.outputFormat == "csv":
                        if args.useContent:
                            results.writerow(
                                [
                                    res.get("LastDownloadTime"),
                                    res.get("LastModificationTimeHeader"),
                                    res.get("URL"),
                                    res.get("FileSize"),
                                    res.get("ETag"),
                                    res.get("FullPath"),
                                    res.get("MD5"),
                                ]
                            )
                        else:
                            results.writerow(
                                [
                                    res.get("LastDownloadTime"),
                                    res.get("LastModificationTimeHeader"),
                                    res.get("URL"),
                                    res.get("FileSize"),
                                    res.get("ETag"),
                                    res.get("FullPath"),
                                ]
                            )
                    elif args.outputFormat == "json":
                        results.append(res)
                    else:
                        results.write(f"{json.dumps(res)}\n")
    if args.outputFormat == "json":
        if isinstance(args.output, str):
            out = open(args.output, "w")
        else:
            out = args.output
        out.write(json.dumps(results))
