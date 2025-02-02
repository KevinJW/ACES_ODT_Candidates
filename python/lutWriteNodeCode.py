### This code is embedded in the nukescript, not accessed from here





import os
import shutil


node = nuke.thisNode()


bakeLuts = nuke.thisNode().knob('bakeLUTs').value()


def cubeToCub(cubePath,cubPath):
    inputCubePath = cubePath
    ouputCubPath = cubPath





    # read the cube
    with open(inputCubePath) as f:
        lines = f.readlines()





    # header
    tlHeader = '''# Truelight Cube v2.1
    # iDims     3
    # oDims     3
    # width     65 65 65\n
    # Cube'''





    # footer
    tlFooter = '''\n# end\n'''






    LUTlines = lines[2:]
    LUTlines = [x.replace('\n','').split(' ') for x in LUTlines]
    LUTlines = [[float(i) for i in x] for x in LUTlines]
    LUTlines = [[str(i) for i in x] for x in LUTlines]





    ## remove decimal from 0.0 and 1.0
    for i, x in enumerate(LUTlines):
        for j, a in enumerate(x):
            if '0.0' == a:
                LUTlines[i][j] = '0'
            if '1.0' == a:
                LUTlines[i][j] = '1'





    # reconstruct the cube string
    stringLUTlines = []
    for line in LUTlines:
        stringLUTlines.append(' '.join(line))
    newLUTStringBlock = '\n'.join(stringLUTlines)





    # join it all up
    outputContents = tlHeader + '\n' + newLUTStringBlock + '\n' + tlFooter





    # check directory for outputCubPath exists, if not, create it
    if not os.path.exists(os.path.dirname(ouputCubPath)):
        os.makedirs(os.path.dirname(ouputCubPath))





    # write the file
    with open(ouputCubPath, 'w') as f:
        f.write(outputContents)





def bakeCandidateLUTfromNode(node):
    candidate = node.knob('candidate').value()
    revision = node.knob('revision').value()
    target = node.knob('target').value()





    nukeScriptDir = nuke.script_directory()
    print(nukeScriptDir)
    templatePath = os.path.join(nukeScriptDir,node.knob('dctlTemplate').evaluate())
    fltransformTemplatePath = os.path.join(nukeScriptDir,node.knob('fltransformTemplate').evaluate())
    flSpacePath = os.path.join(nukeScriptDir,'resources/ACEScct_AP0.flspace')
    print(flSpacePath)





    cubePath = os.path.join(nukeScriptDir,node.knob('cubePath').evaluate())
    ocioCubePath = os.path.join(nukeScriptDir,node.knob('ocioCubePath').evaluate())
    cubPath = os.path.join(nukeScriptDir,node.knob('cubPath').evaluate())
    # replace LUT writer path with evaluated path
    node.knob('file').setValue(cubePath)





    # check cubePath exists, if not, create it
    if not os.path.exists(os.path.dirname(cubePath)):
        os.makedirs(os.path.dirname(cubePath))




    # check ocioCubePath exists, if not, create it
    if not os.path.exists(os.path.dirname(ocioCubePath)):
        os.makedirs(os.path.dirname(ocioCubePath))





    dctlPath = cubePath.replace('.cube','.dctl')
    cubeName = cubePath.split('/').pop(-1)




    if bakeLuts == True:
        node.knob('generate').execute()





    ## write the dctl file
    with open(templatePath) as f:
        lines = f.readlines()
    newLines = [x.replace('replace.cube',cubeName) for x in lines]
    with open(dctlPath, 'w') as f:
        f.write(''.join(newLines))





    # Baselight
    # convert cube to cub
    cubeToCub(cubePath,cubPath)




    # copy cubePath to ocioCubePath
    shutil.copy(cubePath,ocioCubePath)





    ## write the fltransform
    if target == 'Rec709':
        fltransformPath = cubPath.replace('.cub','.fltransform')
        with open(fltransformTemplatePath) as f:
            lines = f.readlines()
        newLines = [x.replace('replaceTransformName','ACES 2.0 Candidate'+ candidate + ' rev'+revision) for x in lines]
        newLines = [x.replace('replaceForward_Rec709.cub',os.path.basename(cubPath)) for x in newLines]
        newLines = [x.replace('replaceForward_Rec2100.cub',os.path.basename(cubPath).replace('Rec709','Rec2100')) for x in newLines]
        with open(fltransformPath, 'w') as f:
            f.write(''.join(newLines))





    # check ACEScct_AP0.flspace exists, if not, copy it
    for flspace in ['/ACEScct_AP0.flspace','/ACEScct_APS4.flspace']:
        ACEScct_AP0_flspace_path = os.path.dirname(cubPath) + flspace
        if not os.path.exists(ACEScct_AP0_flspace_path):
            shutil.copy(flSpacePath,ACEScct_AP0_flspace_path)





def createOCIOconfigs(revision):
    nukeScriptDir = nuke.script_directory()
    revision = nuke.thisNode().knob('revision').value()
    ocioTemplateDir = os.path.join(nukeScriptDir,'resources/')
    newOcioTemplateDir = os.path.join(nukeScriptDir,'OCIO/')
    ocioConfigTemplates = [x for x in os.listdir(ocioTemplateDir) if x.endswith('.ocio')]
    ocioConfigTemplatePaths = [os.path.join(ocioTemplateDir,x) for x in ocioConfigTemplates]
    for config in ocioConfigTemplatePaths:
        configName = config.split('/').pop(-1)
        newConfigName = configName.replace('revXXX','rev'+revision)
        newConfigPath = os.path.join(newOcioTemplateDir,newConfigName)
        with open(config) as f:
            lines = f.readlines()
        newLines = [x.replace('revXXX','rev'+revision) for x in lines]
        with open(newConfigPath, 'w') as f:
            f.write(''.join(newLines))




ODTWrites = []
for node in nuke.allNodes():
    if 'Write_ResolveACES_ODT_LUT' in node.name():
        ODTWrites.append(node)




for ODTWriteNode in ODTWrites:
    bakeCandidateLUTfromNode(ODTWriteNode)




# createOCIOconfigs(revision)
createOCIOconfigs(nuke.thisNode().knob('revision').getValue())