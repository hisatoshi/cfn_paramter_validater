# cfn_paramter_validater

## コンセプト
cloudformaionのテンプレートを作るときに、パラメータ関係でイライラすることがある。
具体的には、

- テンプレート内で参照しているパラメータが未定義
- パラメータファイルを別ファイルに括りだした時に、テンプレートファイルで定義している値がパラメータファイルで未定義

上記の2点に対し、パッと走らせて検出させるプログラム。

## 使い方
```
python cfn_parameter_validater {cfn_filename(.yaml|.json)} {parameter_filename(.yaml|.json)}
```
## depencies
pyyaml
