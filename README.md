# Rise AIO Monitor

Monitor de temperatura para o display do watercooler Rise Aura Ice (`VID:PID aa88:8666`) no Linux.

O serviço lê a temperatura `CPU` do sensor `asusec` quando disponível, faz fallback para outros sensores quando necessário e envia a temperatura para o display via `PyUSB`.

## Estrutura

- `rise_aio_usb_settemp.py`: script principal
- `rise-aio-monitor-wrapper.sh`: wrapper instalado em `/usr/local/bin/rise-aio-monitor`
- `rise-aio-monitor.service`: unit do `systemd`
- `install-rise-aio-systemd.sh`: instala o serviço
- `uninstall-rise-aio-systemd.sh`: remove o serviço
- `rise-aio-monitor-status.sh`: mostra status/logs do serviço
- `requirements.txt`: dependencias Python via `pip`, se preferir

## Dependencias

### Arch Linux

```bash
sudo pacman -S python python-pyusb lm_sensors
```

### Alternativa com pip

```bash
python3 -m pip install -r requirements.txt
```

## Instalacao

No diretorio do projeto:

```bash
sudo ./install-rise-aio-systemd.sh
```

O instalador:

- copia o script para `/usr/local/lib/rise-aio-monitor/rise_aio_usb_settemp.py`
- instala o wrapper em `/usr/local/bin/rise-aio-monitor`
- instala a unit em `/etc/systemd/system/rise-aio-monitor.service`
- habilita e reinicia o servico

## Uso

Ver status:

```bash
./rise-aio-monitor-status.sh
```

Ver logs:

```bash
sudo journalctl -u rise-aio-monitor.service -f
```

Reiniciar:

```bash
sudo systemctl restart rise-aio-monitor.service
```

## Remocao

```bash
sudo ./uninstall-rise-aio-systemd.sh
```
