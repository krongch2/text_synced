#!/usr/bin/env python
# coding=utf-8

from aeneas.executetask import ExecuteTask
from aeneas.task import Task
from PIL import Image
import pysrt
import codecs
import os
import subprocess
import nltk.data
import numpy as np

def create_sub(mp3, txt, srt):
    # config_string = u'task_language=eng|os_task_file_format=srt|is_text_type=mplain'
    # task = Task(config_string=config_string)
    # task.audio_file_path_absolute = mp3
    # task.text_file_path_absolute = txt
    # task.sync_map_file_path_absolute = srt
    # ExecuteTask(task).execute()
    # task.output_sync_map_file()
    os.system('python -m aeneas.tools.execute_task {} {} "task_language=eng|os_task_file_format=srt|is_text_type=plain" {}'.format(mp3, txt, srt))

def text_mod(txt):
    name, ext = os.path.splitext(txt)
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    with codecs.open(txt, encoding='utf-8') as f:
        content = f.read()# .replace('“', '"').replace('”', '"').replace('’', '\'').replace('‘', '\'')
    lines = tolines(tokenizer.tokenize(content))
    lines = tolines(lines)
    with codecs.open(name + 'm' + ext, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(lines))

def tolines(sentences):
    lines = []
    for sentence in sentences:
        islong = len(sentence.split()) > 29
        if islong and '"' in sentence:
            lines += balanced_split('"', sentence)
        elif islong and '–' in sentence:
            lines += balanced_split('–', sentence)
        elif islong and ', ' in sentence:
            lines += balanced_split(', ', sentence)
        else:
            lines += [sentence]
    return lines

def balanced_split(sep, sentence):
    phrases = sentence.split(sep)
    counts = list(map(len, phrases))
    phrases_left = sep.join(phrases[:balanced(counts) + 1]) + sep
    phrases_right = sep.join(phrases[balanced(counts) + 1:])
    return [phrases_left, phrases_right]

def balanced(counts): # return index of the most "balanced" comma
    diff = []
    for i in range(len(counts) - 1):
        left = sum(counts[:i + 1])
        right = sum(counts[i + 1:])
        diff.append(np.abs(left - right))
    return np.argmin(diff)

def cover_mod(cover):
    name, ext = os.path.splitext(cover)
    im = Image.open(cover)
    im_out = Image.open(cover)
    data = im.getdata()
    data_mod = []
    alpha = 0.4
    target = lambda elem: int(alpha * elem + (1 - alpha) * 255)
    for item in data:
        data_mod.append((target(item[0]), target(item[1]), target(item[2])))
    im_out.putdata(data_mod)
    im_out.save(name + 'm' + ext)

def create_mp4(img, mp3, srt, mp4):
    os.system('ffmpeg -loop 1 -i {} -i {} -vf subtitles={} -preset ultrafast -crf 0 -c:a copy -c:v libx264 -shortest {}'.format(img, mp3, srt, mp4))

def compress_mp3(mp3in, mp3out):
    os.system('ffmpeg -i {} -acodec libmp3lame -ac 2 -ab 64k -ar 44100 {}'.format(mp3in, mp3out))

def split_mp3(mp3):
    name, ext = os.path.splitext(mp3)
    # os.system('ffmpeg -ss {} -t {} -i {} {}1.mp3'.format(0, t1, mp3, name))
    # os.system('ffmpeg -ss {} -t {} -i {} {}2.mp3'.format(t1, t2 - t1, mp3, name))
    os.system('ffmpeg -ss {} -t {} -i {} {}3.mp3'.format(0, 20 * 60 + 52, mp3, name))
    # os.system('ffmpeg -ss {} -i {} {}m.mp3'.format(t, mp3, name))

def lin_shift(srt):
    name, ext = os.path.splitext(srt)
    subs = pysrt.open(srt)
    subs.shift(seconds=2*60 + 26.452)
    # subs.shift(seconds=t3)
    subs.save(name + 'm' + ext)
    # part1 = subs.slice(starts_after={'minutes': 0, 'seconds': 0}, ends_before={'minutes': 55, 'seconds': 4})
    # part2 = subs.slice(starts_after={'minutes': 55, 'seconds': 4}, ends_before={'minutes': 71, 'seconds': 13})
    # part2.shift(ratio=1.0001)
    # part1.save('part1.srt')
    # part2.save('part2.srt')

# cover_mod('c.png')
# text_mod('input.txt')
# split_mp3('input.mp3')
# create_sub('input.mp3', 'inputm.txt', 'output.srt')
# compress_mp3('input.mp3', 'inputm.mp3')
# plug "inputm.txt", "inputm.mp3" in webapp
# lin_shift('output.srt')
create_mp4('cm.png', 'input.mp3', 'output.srt', 'output.mp4')
