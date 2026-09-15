ATRIA CURL FARMER — full curl_cffi, no playwright, ~12 detik/akun
================================================================
CARA PAKAI:
  pip install curl_cffi requests
  python3 atria_curl.py 5       # farm 5 akun sekaligus
  python3 atria_curl.py loop    # loop nonstop sampe distop

OUTPUT:
  api_keys.json  (dibuat otomatis di folder yang sama)

ALUR:
  tempmail.elf.biz.id -> Logto register (email+OTP) -> POST /api/keys

TANPA: captcha, playwright, browser. Pure HTTP + TLS fingerprint chrome131.
