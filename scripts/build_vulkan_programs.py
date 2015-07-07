# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------
# drawElements Quality Program utilities
# --------------------------------------
#
# Copyright 2015 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#-------------------------------------------------------------------------

from build.common import *
from build.config import *
from build.build import *

import os
import sys
import string
import argparse
import tempfile
import shutil
import fnmatch

class Module:
	def __init__ (self, name, dirName, binName):
		self.name		= name
		self.dirName	= dirName
		self.binName	= binName

VULKAN_MODULE		= Module("dEQP-VK",		"vulkan",		"deqp-vk")
DEFAULT_BUILD_DIR	= os.path.join(tempfile.gettempdir(), "vulkan-programs", "{targetName}-{buildType}")
DEFAULT_TARGET		= "null"
DEFAULT_DST_DIR		= os.path.join(DEQP_DIR, "data", "vulkan", "prebuilt")

def getBuildConfig (buildPathPtrn, targetName, buildType):
	buildPath = buildPathPtrn.format(
		targetName	= targetName,
		buildType	= buildType)

	return BuildConfig(buildPath, buildType, ["-DDEQP_TARGET=%s" % targetName])

def cleanDstDir (dstPath):
	binFiles = [f for f in os.listdir(dstPath) if os.path.isfile(os.path.join(dstPath, f)) and fnmatch.fnmatch(f, "*.spirv")]

	for binFile in binFiles:
		print "Removing %s" % os.path.join(dstPath, binFile)
		os.remove(os.path.join(dstPath, binFile))

def execBuildPrograms (buildCfg, generator, module, mode, dstPath):
	workDir = os.path.join(buildCfg.getBuildDir(), "modules", module.dirName)

	pushWorkingDir(workDir)

	try:
		binPath = generator.getBinaryPath(buildCfg.getBuildType(), os.path.join(".", "vk-build-programs"))
		execute([binPath, "--mode", mode, "--dst-path", dstPath])
	finally:
		popWorkingDir()

def parseArgs ():
	parser = argparse.ArgumentParser(description = "Build SPIR-V programs",
									 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("-b",
						"--build-dir",
						dest="buildDir",
						default=DEFAULT_BUILD_DIR,
						help="Temporary build directory")
	parser.add_argument("-t",
						"--build-type",
						dest="buildType",
						default="Debug",
						help="Build type")
	parser.add_argument("-c",
						"--deqp-target",
						dest="targetName",
						default=DEFAULT_TARGET,
						help="dEQP build target")
	parser.add_argument("--mode",
						dest="mode",
						default="build",
						help="Build mode (build or verify)")
	parser.add_argument("-d",
						"--dst-path",
						dest="dstPath",
						default=DEFAULT_DST_DIR,
						help="Destination path")
	return parser.parse_args()

if __name__ == "__main__":
	args = parseArgs()

	generator	= ANY_GENERATOR
	buildCfg	= getBuildConfig(args.buildDir, args.targetName, args.buildType)
	module		= VULKAN_MODULE

	build(buildCfg, generator, ["vk-build-programs"])

	if args.mode == "build":
		if os.path.exists(args.dstPath):
			cleanDstDir(args.dstPath)
		else:
			os.makedirs(args.dstPath)

	execBuildPrograms(buildCfg, generator, module, args.mode, args.dstPath)