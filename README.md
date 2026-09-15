# Atria Curl Farmer

Pure curl_cffi, no playwright. ~12 detik/akun.

## Install

```
pip install curl_cffi requests
```

## Usage

```
python3 atria_curl.py 5       # farm 5 akun sekaligus
python3 atria_curl.py loop    # loop nonstop sampe distop
```

## Output

`api_keys.json` — dibuat otomatis di folder yang sama.

## Flow

tempmail.elf.biz.id → Logto register (email+OTP) → POST /api/keys

Tanpa captcha, playwright, browser. Pure HTTP + TLS fingerprint chrome131.

## Contact

- Telegram: [@elman14](https://t.me/elman14)
- Channel: [@elfgank](https://t.me/elfgank)
