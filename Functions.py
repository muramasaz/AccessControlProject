__author__ = 'mysterylz'
#Function__
import operator


def newdatasequence(olddata, datasize):
    newdata = list(olddata)
    olddata = list(newdata)

    if datasize == 4:
        newdata[0] = olddata[2]
        newdata[1] = olddata[3]
        newdata[2] = olddata[0]
        newdata[3] = olddata[1]
        return reduce(operator.add, newdata)

    elif datasize == 6:
        newdata[0] = olddata[4]
        newdata[1] = olddata[5]
        newdata[2] = olddata[2]
        newdata[3] = olddata[3]
        newdata[4] = olddata[0]
        newdata[5] = olddata[1]
        return reduce(operator.add, newdata)

    elif datasize == 8:
        newdata[0] = olddata[6]
        newdata[1] = olddata[7]
        newdata[2] = olddata[4]
        newdata[3] = olddata[5]
        newdata[4] = olddata[2]
        newdata[5] = olddata[3]
        newdata[6] = olddata[0]
        newdata[7] = olddata[1]
        return reduce(operator.add, newdata)

    elif datasize == 10:
        newdata[0] = olddata[8]
        newdata[1] = olddata[9]
        newdata[2] = olddata[6]
        newdata[3] = olddata[7]
        newdata[4] = olddata[4]
        newdata[5] = olddata[5]
        newdata[6] = olddata[2]
        newdata[7] = olddata[3]
        newdata[8] = olddata[0]
        newdata[9] = olddata[1]
        return reduce(operator.add, newdata)

    elif datasize == 12:
        newdata[0] = olddata[10]
        newdata[1] = olddata[11]
        newdata[2] = olddata[8]
        newdata[3] = olddata[9]
        newdata[4] = olddata[6]
        newdata[5] = olddata[7]
        newdata[6] = olddata[4]
        newdata[7] = olddata[5]
        newdata[8] = olddata[2]
        newdata[9] = olddata[3]
        newdata[10] = olddata[0]
        newdata[11] = olddata[1]
        return reduce(operator.add, newdata)
    else:
        return False

def deleteunusedata(lendata, data, lsb):
    hexset = "0123456789ABCDEF"
    tmp = list(data)
    lentmp = len(data)

    if hexset.find(tmp[len(tmp)-1]) < 0:
        tmp = tmp[:-1]
        lentmp = len(tmp)
    i = lentmp

    if lsb == 0:
        i = 0
        while i < (lentmp - lendata):
            tmp.pop(0)
            i += 1
        return reduce(operator.add, tmp)
    elif lsb == 1:
        while i > lendata:
            lentmp -= 1
            tmp.pop(lentmp)
            i -= 1
        return reduce(operator.add, tmp)
    else:
        return False
