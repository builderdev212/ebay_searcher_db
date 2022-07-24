import re

data = ['https://ebay.com/itm/123456?hash=item28caef0a3a:g:E3kAAOSwlGJiMikD&amdata=enc%3AAQAHAAAAsJoWXGf0hxNZspTmhb8%2FTJCCurAWCHuXJ2Xi3S9cwXL6BX04zSEiVaDMCvsUbApftgXEAHGJU1ZGugZO%2FnW1U7Gb6vgoL%2BmXlqCbLkwoZfF3AUAK8YvJ5B4%2BnhFA7ID4dxpYs4jjExEnN5SR2g1mQe7QtLkmGt%2FZ%2FbH2W62cXPuKbf550ExbnBPO2QJyZTXYCuw5KVkMdFMDuoB4p3FwJKcSPzez5kyQyVjyiIq6PB2q%7Ctkp%3ABlBMULq7kqyXYA', 'https://www.ebay.com/itm/394171795011?epid=2296430657&hash=item5bc6784643:g:ShsAAOSwS0ti2EHG', 'https://www.ebay.com/itm/195150651995?epid=27026650224&hash=item2d6fe2a25b:g:~SkAAOSw4fFir3Xo&amdata=enc%3AAQAHAAAA4OWES%2FBb3SV7vDaRu60n6DgqP2954gaYV2dcS4Dyv57KHzYCN3xp1pDMp4m%2Ffrek1I9nrdDKRvKyyKHd5k148womvF3DHjjpjNKUdOjglsJK1z7fJ6TxTNWxtXxF%2BS25%2Fb9KFP4g%2BSKx10%2FttASSQysbTuThvo79s9jhNSShaMgCbaszVh78XS8eM21n8RlfDmIMrwSA%2FNoKNOUEG9ieSmhM1JI%2Bcp%2B4rJ9zAJqAsk%2Ff4BvNn2XC8Wat9QiNSwj6mH6DAe2GhTtJkcliyNujf7MnridyPN8vJ%2BKgdwX6gfXT%7Ctkp%3ABFBMsNvQxcVg', 'https://www.ebay.com/itm/255631950925?epid=28027617335&hash=item3b84da044d:g:cn0AAOSwkS5i0jDR']

for val in data:
    print(re.findall(r"^.*\?", val)[0][:-1])
