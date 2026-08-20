# 认证测试附件

此目录用于本机存放认证资料填写用的模拟附件。请勿放入真实个人证件或生产资料，也不要将附件提交到版本库。

运行 `WEB-011` 的资料填写阶段前，请准备以下 3 个文件：

| 文件名 | 内容 | 格式与大小 |
| --- | --- | --- |
| `business_license.png` | 模拟统一社会信用代码证 | PNG/JPG/JPEG/PDF，不超过 2 MB |
| `legal_representative_id.png` | 模拟法定代表人证件 | PNG/JPG/JPEG/PDF，不超过 2 MB |
| `operator_id.png` | 模拟经办人证件 | PNG/JPG/JPEG/PDF，不超过 2 MB |

建议图片上醒目标注“自动化测试模拟资料，无真实效力”，并确保内容与 `data/data_provider_certification.json` 中的模拟字段一致。

## 数据产品测试素材

`data_product_cover.png` 是数据产品新增用例使用的通用模拟封面，图片已标注“自动化测试模拟产品”。不得替换为真实产品图片或客户资料。

## 产品订单合同素材

`mock_data_product_purchase_contract.docx` 是 WEB-082 使用的模拟合同，正文明确标注“仅用于自动化测试，不构成真实商业合同”。可通过以下命令重新生成：

```powershell
python test_materials/build_mock_product_contract.py
```

不得将该文件替换为真实合同、客户资料、签章文件或付款凭证。

## 支付凭证测试素材

`mock_payment_voucher.pdf` 是 WEB-083 使用的模拟支付凭证，醒目标注“仅供自动化测试、无真实支付效力”，且不包含任何银行账户、客户身份、签章或真实交易数据。可通过以下命令重新生成：

```powershell
python test_materials/build_mock_payment_voucher.py
```

不得将该文件替换为真实付款凭证、银行流水、账户信息或客户资料。
