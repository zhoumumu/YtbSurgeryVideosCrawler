# File Generating Log

## 5.24

vids.txt -> vidInfo.csv 高质量两万条

## 5.27

商讨确定类别标签体系，这几个文件都不是最终版本，持续refine 10cates.txt

## 5.30

终版基于术语的分类结果引入投票机制，得到vidInfo_rawClassfied.csv
其他文件都是副产物

## 6.3

7个低质量playlist(含多个)视频源（lowQualitySrcPlaylist.csv）
手工筛选出lowQualityPlaylist.csv和singles.csv
lowQualityPlaylist.csv -> vids_low_multi.txt
vids_low_multi.txt + singles.csv = vids2.txt
vids2.txt -> vidInfo2.csv
vidInfo2.csv -> vidInfo_rawClassfied2.csv -> 手工补上singles.csv的分类，根据lowQualityPlaylist.csv的记录分析过滤非手术视频

## 6.13

剩余channel source（lowQualitySrcChannel.csv）// 里面混入了一个视频链接手动修改过了
爬信息过程合并->vidInfo3.csv，后续用脚本去过重了
上面爬断了的部分条目处理完NULL->samples.csv 用于分析topc catagory
翻译并打上数字标签->vidInfo3_rawClassified.csv -> vids3.txt