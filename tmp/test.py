def extract_txt_from_pdf3(fp, tgt_path):

    """
    Desc: 读取pdf文件中的文本内容，并对文本内容进行简单清洗
    input: file_path
    return: str
    """
    # from colorful import print亮黄, print亮绿
    text = 0  # Index 0 文本
    font_size = 1  # Index 1 字体
    bbox = 2  # Index 2 框框
    REMOVE_FOOT_NOTE = True  # 是否丢弃掉 不是正文的内容 （比正文字体小，如参考文献、脚注、图注等）
    REMOVE_FOOT_FFSIZE_PERCENT = 0.97  # 小于正文的？时，判定为不是正文（有些文章的正文部分字体大小不是100%统一的，有肉眼不可见的小变化）

    def primary_ffont_size(line):
        """
        提取文本块主字体
        将每种字体存为一个key，字符数为value，每种字体大小的字符数相加，最多的那个就是主字体，
        """
        font_size_statiscs = {}
        for span in line['spans']:
            if span['size'] not in font_size_statiscs:
                font_size_statiscs[span['size']] = 0
            font_size_statiscs[span['size']] += len(span['text'])
        return max(font_size_statiscs, key=font_size_statiscs.get)

    def ffont_size_same(a, b):
        """
        提取字体大小是否近似相等
        """
        return abs((a - b) / max(a, b)) < 0.02

    with fitz.open(fp) as doc:
        meta_txt = []
        meta_font = []

        meta_line = []
        meta_span = []
        for index, page in enumerate(doc):
            text_areas = page.get_text("dict")  # 获取页面上的文本信息
            for block in text_areas['blocks']:
                if 'lines' in block:
                    lines = block['lines']

                    # 提取每一行的文本信息、主字体大小、框框信息、行原始信息
                    for line in lines:
                        txt_line = "".join([span['text'] for span in line['spans']])
                        if len(txt_line) == 0:
                            continue
                        Primary_fontsize = primary_ffont_size(line)
                        meta_line.append([txt_line, Primary_fontsize, line['bbox'], line])
                        for span in line['spans']:
                            meta_span.append([span['text'], span['size'], len(span['text'])])

                    # 提取整个块的文本
                    texts = []
                    for line in lines:
                        line_text = ""
                        for span in line['spans']:
                            line_text += span['text']
                        texts.append(line_text)
                    block_text = " ".join(texts).replace('- ', '')
                    meta_txt.append(block_text)

                    #  计算整个块的平均字体大小
                    sizes = []
                    for line in lines:
                        line_sizes = [span['size'] for span in line['spans']]
                        sizes.append(np.mean(line_sizes))
                    block_size = np.mean(sizes)
                    meta_font.append(block_size)

        font_size_statiscs = {}
        for span in meta_span:
            if span[1] not in font_size_statiscs:
                font_size_statiscs[span[1]] = 0
            font_size_statiscs[span[1]] += span[2]
        main_font_size = max(font_size_statiscs, key=font_size_statiscs.get)
        if REMOVE_FOOT_NOTE:
            give_up_fize_threshold = main_font_size * REMOVE_FOOT_FFSIZE_PERCENT

        mega_sec = []
        sec = []
        for index, line in enumerate(meta_line):
            # 丢弃掉不是正文的内容
            import regex
            pattern = regex.compile(r'^[0-9\p{P}\p{S}()（）\[\]{}&#8203;``【oaicite:1】``&#8203;]+$', re.UNICODE)
            # pattern = re.compile(r'^[0-9\p{P}\p{S}\uff08\uff09\u3008\u3009\uff1b\uff1d\uff5b\uff5d\u200B``【oaicite:1】``]+$', re.UNICODE)
            if pattern.fullmatch(line[text]):
                continue
            #
            if index == 0:
                sec.append(line[text])
                continue
            if REMOVE_FOOT_NOTE:
                current_font_size = meta_line[index][font_size]
                pre_font_size = meta_line[index - 1][font_size]
                if current_font_size <= give_up_fize_threshold:
                    continue
            #
            if ffont_size_same(current_font_size, pre_font_size):
                # 尝试识别段落
                if re.match(r'.*[\.。]', meta_line[index][text]) and \
                        (meta_line[index - 1][text] != 'NEW_BLOCK') and \
                        (meta_line[index][bbox][2] - meta_line[index][bbox][0]) < (
                        meta_line[index - 1][bbox][2] - meta_line[index - 1][bbox][0]) * 0.8:
                    sec[-1] += line[text]
                    sec[-1] += "\n\n"
                else:

                    # sec[-1] += " "
                    sec[-1] += ""

                    sec[-1] += line[text]
            else:
                if (index + 1 < len(meta_line)) and \
                        meta_line[index][font_size] > main_font_size:
                    # 单行 + 字体大
                    mega_sec.append(copy.deepcopy(sec))
                    sec = []
                    if not re.match('第[一二三四五六七八九十\d]+章|[一二三四五六七八九十]、', line[text]):
                        sec.append("# " + line[text])
                    else:
                        sec.append(line[text])
                else:
                    # 尝试识别section
                    if meta_line[index - 1][font_size] > meta_line[index][font_size]:
                        sec.append("\n" + line[text])
                    else:
                        sec.append(line[text])
        mega_sec.append(copy.deepcopy(sec))

        finals = []
        for ms in mega_sec:
            # if re.match(r'^#.*$', ms[0]):
            #     ms[0] = ms[0] + "\n"
            # if re.match(r'^[一二三四五六七八九十]、|^[\((][(\d{1,2})一二三四五六七八九十][）\)]', ms[0]):
            #      ms[0] = ms[0] + "\n"
            
            # 使用正则表达式去掉开头和末尾的所有空格
            # ms = re.sub(r'^\s*|\s*$', '', ms)
            final = " ".join(ms)
            final = final.replace('- ', ' ')

            final = re.sub(r'^\s*|\s*$', '', final)
            
            finals.append(final)
        meta_txt = finals
        def clean_short_text_blocks(meta_txt):
            for index, block_txt in enumerate(meta_txt):
                if len(block_txt) < 10:
                    meta_txt[index] = '\n'
            return meta_txt

        meta_txt = clean_short_text_blocks(meta_txt)
       

        meta_txt = '\n'.join(meta_txt)
        meta_txt = remove_extra_newlines(meta_txt)

        # # 为类似“一、”之类的模式前面添加换行符
        # pattern = re.compile(r"(?<!)([一二三四五六七八九十]、)") # 123456789
        # meta_txt = re.sub(pattern, r"\n\1", meta_txt)

        # # 删除“一、”后面的空格
        # pattern = re.compile(r"(?<=[一二三四五六七八九十123456789]、)\s")
        # meta_txt = re.sub(pattern, "", meta_txt)

        # # 为类似“（一）”之类的模式前面添加换行符
        # pattern = re.compile(r"(?<!\n)(（[一二三四五六七八九十]）)")
        # meta_txt = re.sub(pattern, r"\n\1", meta_txt)

        # # 删除“（一）”后面的空格
        # pattern = re.compile(r"(?<=（[一二三四五六七八九十]）)\s")
        # meta_txt = re.sub(pattern, "", meta_txt)

        # # 替换模式
        # pattern = re.compile(r"([一二三四五六七八九十]、.*?) ")                                                  
        # # 进行替换
        # meta_txt = pattern.sub(r"\n\1\n", meta_txt)

        # pattern2 = re.compile(r"(（[一二三四五六七八九十]）.*? )")
        # meta_txt = pattern2.sub(r"\n\1\n", meta_txt)
        final_result = re.sub(r"[\r\n]+", "\n", meta_txt)

    
    # 保存
    base_fn = os.path.basename(fp).lower().replace('.pdf', '.txt')  
    with open(os.path.join(tgt_path, base_fn), 'w') as f:
        f.write(final_result)

    return final_result