#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Manuel Bastioni, Marc Flerackers, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2015

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

    This file is part of MakeHuman (www.makehuman.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------
Import/Export module that uses JSON text to read in values for modifiers.

TODO
- get undo/redo functioning
"""

import gui3d
import gui
from core import G
import mh
import log
import os
from codecs import open
import json

from debugdump import DebugDump
import math


measures = {}
measures['measure/measure-neck-circ-decr|incr'] = [7514,10358,7631,7496,7488,7489,7474,7475,7531,7537,7543,7549,7555,7561,7743,7722,856,1030,1051,850,844,838,832,826,820,756,755,770,769,777,929,3690,804,800,808,801,799,803,7513,7515,7521,7514]
measures['measure/measure-neck-height-decr|incr'] = [853,854,855,856,857,858,1496,1491]


measures['measure/measure-upperarm-circ-decr|incr']=[8383,8393,8392,8391,8390,8394,8395,8399,10455,10516,8396,8397,8398,8388,8387,8386,10431,8385,8384,8389]
measures['measure/measure-upperarm-length-decr|incr'] = [8274,10037]

measures['measure/measure-lowerarm-length-decr|incr'] = [10040,10548]
measures['measure/measure-wrist-circ-decr|incr']=[10208,10211,10212,10216,10471,10533,10213,10214,10215,10205,10204,10203,10437,10202,10201,10206,10200,10210,10209,10208]

measures['measure/measure-frontchest-dist-decr|incr']=[1437,8125]
measures['measure/measure-bust-circ-decr|incr']=[8439,8455,8462,8446,8478,8494,8557,8510,8526,8542,10720,10601,10603,10602,10612,10611,10610,10613,10604,10605,10606,3942,3941,3940,3950,3947,3948,3949,3938,3939,3937,4065,1870,1854,1838,1885,1822,1806,1774,1790,1783,1767,1799,8471]
measures['measure/measure-underbust-circ-decr|incr'] = [10750,10744,10724,10725,10748,10722,10640,10642,10641,10651,10650,10649,10652,10643,10644,10645,10646,10647,10648,3988,3987,3986,3985,3984,3983,3982,3992,3989,3990,3991,3980,3981,3979,4067,4098,4073,4072,4094,4100,4082,4088, 4088]
measures['measure/measure-waist-circ-decr|incr'] = [4121,10760,10757,10777,10776,10779,10780,10778,10781,10771,10773,10772,10775,10774,10814,10834,10816,10817,10818,10819,10820,10821,4181,4180,4179,4178,4177,4176,4175,4196,4173,4131,4132,4129,4130,4128,4138,4135,4137,4136,4133,4134,4108,4113,4118,4121]
measures['measure/measure-napetowaist-dist-decr|incr']=[1491,4181]
measures['measure/measure-waisttohip-dist-decr|incr']=[4121,4341]
measures['measure/measure-shoulder-dist-decr|incr'] = [7478,8274]

measures['measure/measure-hips-circ-decr|incr'] = [4341,10968,10969,10971,10970,10967,10928,10927,10925,10926,10923,10924,10868,10875,10861,10862,4228,4227,4226,4242,4234,4294,4293,4296,4295,4297,4298,4342,4345,4346,4344,4343,4361,4341]

measures['measure/measure-upperleg-height-decr|incr'] = [10970,11230]
measures['measure/measure-thigh-circ-decr|incr'] = [11071,11080,11081,11086,11076,11077,11074,11075,11072,11073,11069,11070,11087,11085,11084,12994,11083,11082,11079,11071]

measures['measure/measure-lowerleg-height-decr|incr'] = [11225,12820]
measures['measure/measure-calf-circ-decr|incr'] = [11339,11336,11353,11351,11350,13008,11349,11348,11345,11337,11344,11346,11347,11352,11342,11343,11340,11341,11338,11339]

measures['measure/measure-ankle-circ-decr|incr'] = [11460,11464,11458,11459,11419,11418,12958,12965,12960,12963,12961,12962,12964,12927,13028,12957,11463,11461,11457,11460]
measures['measure/measure-knee-circ-decr|incr'] = [11223,11230,11232,11233,11238,11228,11229,11226,11227,11224,11225,11221,11222,11239,11237,11236,13002,11235,11234,11223]

class ImportAction(gui3d.Action):
    def __init__(self, human, before, after):
        super(ImportAction, self).__init__("Import")
        self.human = human
        self.before = before
        self.after = after

    def do(self):
        self._assignModifierValues(self.after)
        return True

    def undo(self):
        self._assignModifierValues(self.before)
        return True

    def _assignModifierValues(self, valuesDict):
        _tmp = self.human.symmetryModeEnabled
        self.human.symmetryModeEnabled = False
        for mName, val in valuesDict.items():
            try:
                self.human.getModifier(mName).setValue(val)
            except:
                pass
        self.human.applyAllTargets()
        self.human.symmetryModeEnabled = _tmp

class ImportTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Import Measurements')
        self.human = G.app.selectedHuman
        toolbox = self.addLeftWidget(gui.SliderBox('Import JSON'))
        self.loadButton = toolbox.addWidget(gui.BrowseButton(mode='open'), 0, 0)
        self.loadButton.setLabel('Load ...')
        self.loadButton.directory = mh.getPath()
        self.saveAsButton = toolbox.addWidget(gui.Button('Save As...'), 2, 0)
        
        @self.loadButton.mhEvent
        def onClicked(filename):
            if not filename:
                return
            if(os.path.exists(filename)):
                # read in json information
                contents = open(filename, 'rU', encoding="utf-8").read()
                log.debug('File contents read')       
                newMeasurements = json.loads(contents)    
                # validate/process the new measurements
                #oldValues = dict( [(m.fullName, m.getValue()) for m in self.human.modifiers] )
                newValues, oldValues = processMeaurements(self.human,  newMeasurements)
                log.debug("File imported for measurements")
                # apply new measurements
                gui3d.app.do( ImportAction(self.human, oldValues, newValues) )
                log.debug("Imported measurements have been applied")
                self.filename = filename
                self.directory = os.path.split(filename)[0]
                log.debug(oldValues)
                for key, value in newValues.iteritems():
                    if key in measures:
                        DebugDump().appendMessage('{0}: {1}'.format(key, str(getMeasure(self.human, key, 'metric'))))
   
            else:
                log.debug("Imported measurements have been not been applied, file does not exist")

        @self.saveAsButton.mhEvent
        def onClicked(event):
            filename = mh.getSaveFileName(
                mh.getPath(),
                'JSON File (*.json);;All files (*.*)')
            if filename:
                doSave(filename)

        
        
def doSave(filename):
    # get modifier information as JSON
    currentValues = dict( [(m.fullName.encode('ascii','replace'), m.getValue()) for m in G.app.selectedHuman.modifiers] )
    # save out JSON data
    with open(filename, 'w') as outfile:
        json.dump(currentValues, outfile, indent=4, sort_keys=True)
    log.debug("Measurements information saved to %s" % filename)

def processMeaurements(human,  newMeasurements) :
    oldValues = dict( [(m.fullName, m.getValue()) for m in human.modifiers] )
    newValues = oldValues
    
    # update values in newValues to reflect new measurements
    for mod, v in newMeasurements.items():
        m = human.getModifier(mod)
        if v < m.getMin() or v > m.getMax():
            newValue = m.getDefaultValue()
        else:
            newValue = v
        newValues[m.fullName] = newValue



        DebugDump().appendMessage(m.fullName)
        DebugDump().appendMessage(str(newValue))
        if m.fullName in measures:
            DebugDump().appendMessage(str(getMeasure(human, m.fullName, 'metric')))




        # apply value to opposite side, if it exists
        symm = m.getSymmetricOpposite()
        if symm and symm not in newValues:
            m2 = human.getModifier(symm)
            if v < m2.getMin() or v > m2.getMax():
                newValue = m2.getDefaultValue()
            else:
                newValue = v
            newValues[m2.fullName] = newValue

    # prevent pregnancy for male, too young or too old subjects
    if newValues.get("macrodetails/Gender", 0) > 0.5 or \
       newValues.get("macrodetails/Age", 0.5) < 0.2 or \
       newValues.get("macrodetails/Age", 0.7) < 0.75:
        if "stomach/stomach-pregnant-decr|incr" in newValues:
            newValues["stomach/stomach-pregnant-decr|incr"] = 0

    # prevent total ehtnicity values being greater than 1 (linked together)
    ehtnicities = ["macrodetails/African", "macrodetails/Asian", "macrodetails/Caucasian"]
    totalEthnicity = newValues["macrodetails/African"] + newValues["macrodetails/Asian"] + newValues["macrodetails/Caucasian"]
    log.debug(totalEthnicity)
    
    if totalEthnicity == 0:
        # reset ehtnicities to default values
        for e in ehtnicities:
            mod = human.getModifier(e)
            newValues[mod.fullName] = mod.getDefaultValue()
    elif totalEthnicity != 1:
        log.debug('not equal to 1')
         #scale each ethnicity to a valid value
        for e in ehtnicities:
            adjustedValue = newValues[e] * (1.0/ totalEthnicity)
            newValues[e] = adjustedValue

    #return new measurements
    return newValues, oldValues

# used for scaling ehtnicities to valid values
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def load(app):
    category = app.getCategory('Modelling')
    taskview = category.addTask(ImportTaskView(category))

def unload(app):
    pass

def getMeasure(human, measurementname, mode):

    measure = 0
    vindex1 = measures[measurementname][0]
    for vindex2 in measures[measurementname]:
        vec = human.meshData.coord[vindex1] - human.meshData.coord[vindex2]
        measure += math.sqrt(vec.dot(vec))
        vindex1 = vindex2

    if mode == 'metric':
        return 10.0 * measure
    else:
        return 10.0 * measure * 0.393700787
