"""Disk layout representation of a virtual machine.

Parses a disk layout and 

Usage:
layout = DiskLayout(vm)
for (ctrl_nr, slot_nr, disk) in layout:
    print "%s-%s" % (ctrl_nr, slot_nr)

"""
from pyVmomi import vim

class DiskLayout(object):
    def __init__(self, vm):
        self.layout = {}
        self.__layout(vm)

    def del_slot(self, ctrl_nr, slot_nr):
        layout = self.layout
        try:
            del layout[ctrl_nr]["slots"][slot_nr]
        except KeyError:
            pass

    def get_controller(self, ctrl_nr):
        layout = self.layout
        ctrl = None
        try:
            ctrl = layout[ctrl_nr]["ctrl"]
        except KeyError:
            pass
        return ctrl

    def add_controller(self, ctrl_nr, ctrl):
        layout = self.layout
        assert ctrl_nr not in layout, "%d" % (ctrl_nr)
        layout[ctrl_nr] = {"ctrl": ctrl, "slots": {}}

    def add_disk(self, ctrl_nr, slot_nr, disk):
        layout = self.layout
        assert ctrl_nr in layout and slot_nr not in layout[ctrl_nr]["slots"], \
                "%d-%d" % (ctrl_nr, slot_nr)
        layout[ctrl_nr]["slots"][slot_nr] = disk

    def get_disk(self, ctrl_nr, slot_nr):
        layout = self.layout
        disk = None
        try:
            disk = layout[ctrl_nr]["slots"][slot_nr]
        except KeyError:
            pass
        return disk

    def get_free_slot(self):
        layout = self.layout
        for ctrl_nr in sorted(layout.keys()):
            slotList = layout[ctrl_nr]["slots"]
            for slot_nr in range(0, 16): # slots per controller 16
                if slot_nr not in slotList.keys():
                    return ctrl_nr, slot_nr
        assert False, "%d-%d" % (ctrl_nr, slot_nr)

    def __iter__(self):
        layout = self.layout
        for ctrl_nr in sorted(layout.keys()):
            slot_list = layout[ctrl_nr]["slots"]
            for slot_nr in sorted(slot_list.keys()):
                disk = layout[ctrl_nr]["slots"][slot_nr]
                yield (ctrl_nr, slot_nr, disk)

    def __layout(self, vm):
        # layout:
        res = {}
        ctrls = []
        disks = []
        for dev in vm.config.hardware.device:
            # vim.vm.device.VirtualController
            # vim.vm.device.VirtualIDEController
            # vim.vm.device.VirtualSCSIController
            if isinstance(dev, vim.vm.device.VirtualSCSIController):
                ctrls.append(dev)
            if isinstance(dev, vim.vm.device.VirtualDisk):
                disks.append(dev)
        for ctrl_nr in range(0, len(ctrls)):
            ctrl = ctrls[ctrl_nr]
            ctrl_disks = [x for x in disks if x.key in ctrl.device]
            self.add_controller(ctrl_nr, ctrl)
            for disk in ctrl_disks:
                self.add_disk(ctrl_nr, disk.unitNumber, disk)

