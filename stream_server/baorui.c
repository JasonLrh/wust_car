template<typename IMG, typename IMG_CHNN>
void GetBinaryImage(IMG *res, IMG &src, IMG_CHNN chnn, int s = -1, int t = -1, bool cpy = true)
{
    if (res == NULL)                                // 搞到合适的原图
    {
        res = &src;
    }
    else if (cpy)
    {
        res->CopyFrom(src);
    }
    else {
        *res = src;
    }
    auto &img = *res;
    // 默认参数是s = width / 8, t = 15
    const uint32_t w = img.Width();
    const uint32_t h = img.Height();
    if (s == -1)
    {
        s = (int)(w / 8);
    }
    if (t == -1)
    {
        t = 15;
    }
    //
    uint32_t *intImg = new uint32_t[w * h];
    memset(intImg, 0, w * h * sizeof(uint32_t));
    auto intImgAt = [&](int i, int j) -> uint32_t&
    {
        static uint32_t zero = 0;
        if (i < 0)
        {
            return zero;
        }
        if (j < 0)
        {
            return zero;
        }
        return *(intImg + j * (int)(w)+i);
    };
    //
    for (uint32_t i = 0; i < w; i += 1)             // 构造积分图
    {
        uint32_t sum = 0;
        for (uint32_t j = 0; j < h; j += 1)
        {
            sum += (uint32_t)img(i, j, chnn);
            if (i == 0)
            {
                intImgAt(i, j) = sum;
            }
            else {
                intImgAt(i, j) = intImgAt(i - 1, j) + sum;
            }
        }
    }
    for (int i = 0; i < (int)w; i += 1)             // 按照积分图进行二值化
    {
        for (int j = 0; j < (int)h; j += 1)
        {
            const uint32_t x1 = img.Range(i - s / 2, w);
            const uint32_t x2 = img.Range(i + s / 2, w);
            const uint32_t y1 = img.Range(j - s / 2, h);
            const uint32_t y2 = img.Range(j + s / 2, h);
            const uint32_t cnt = (x2 - x1) * (y2 - y1);
            const uint32_t sum = intImgAt(x2, y2) - intImgAt(x2, y1 - 1)
                - intImgAt(x1 - 1, y2) + intImgAt(x1 - 1, y1 - 1);
            const uint32_t cur = src(i, j, chnn);
            if ((cur * cnt) <= (uint32_t)(sum * ((100.0f - (float32)t) / 100.0f)))
            {
                img(i, j, chnn) = 0;
            }
            else {
                img(i, j, chnn) = 0xff;
            }
        }
    }
}