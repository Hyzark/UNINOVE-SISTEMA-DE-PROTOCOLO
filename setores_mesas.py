class Setor:
    def __init__(self, id_setor, nome):
        self.id_setor = id_setor
        self.nome = nome
        self.mesas = []

    def adicionar_mesa(self, mesa):
        self.mesas.append(mesa)

    def listar_mesas(self):
        print(f"\nSetor: {self.nome}")
        for mesa in self.mesas:
            print(f" - Mesa {mesa.nome}, responsável: {mesa.responsavel}")


class Mesa:
    def __init__(self, id_mesa, nome, responsavel):
        self.id_mesa = id_mesa
        self.nome = nome
        self.responsavel = responsavel
        self.processo = []

    def receber_processo(self, protocolo):
        self.processo.append(protocolo)
        print(f"Processo {protocolo} recebido na Mesa {self.nome}")

    def listar_processos(self):
        print(f"\nProcessos da Mesa {self.nome}:")
        if not self.processo:
            print("Nenhum processo.")
        else:
            for proc in self.processo:
                print(f" - {proc}")



setor_financeiro = Setor(1, "Financeiro")

mesa_01 = Mesa(1, "Prestação de Contas", "Maria Silva")
mesa_01.receber_processo("PROC-2026-0001")

mesa_02 = Mesa(2, "Contas a Pagar", "João Carlos")
mesa_02.receber_processo("PROC-2026-0002")

mesa_03 = Mesa(3, "Contas a Receber", "David Aquino")
mesa_03.receber_processo("PROC-2026-0003")

mesa_04 = Mesa(4, "Reembolso", "Pedro Croitor")

mesa_05 = Mesa(5, "Pagamentos", "Milena Oliveira")
mesa_05.receber_processo("PROC-2026-0004")
mesa_05.receber_processo("PROC-2026-0005")

setor_financeiro.adicionar_mesa(mesa_01)
setor_financeiro.adicionar_mesa(mesa_02)
setor_financeiro.adicionar_mesa(mesa_03)
setor_financeiro.adicionar_mesa(mesa_04)
setor_financeiro.adicionar_mesa(mesa_05)


setor_rh = Setor(2, "RH")

mesa_06 = Mesa(6, "Recrutamento e Seleção", "Gabriella Perreira")
mesa_06.receber_processo("PROC-2026-0006")

mesa_07 = Mesa(7, "Admissão", "Gabriel Lins")
mesa_07.receber_processo("PROC-2026-0007")

mesa_08 = Mesa(8, "Folha de Pagamento", "Anna Souza")
mesa_08.receber_processo("PROC-2026-0008")

mesa_09 = Mesa(9, "Férias", "Beatriz Silva")

mesa_10 = Mesa(10, "Benefícios", "Gabriel Rodrigues")
mesa_10.receber_processo("PROC-2026-0009")

mesa_11 = Mesa(11, "Desligamento", "Jonathan Jesus")
mesa_11.receber_processo("PROC-2026-0010")
mesa_11.receber_processo("PROC-2026-0011")

setor_rh.adicionar_mesa(mesa_06)
setor_rh.adicionar_mesa(mesa_07)
setor_rh.adicionar_mesa(mesa_08)
setor_rh.adicionar_mesa(mesa_09)
setor_rh.adicionar_mesa(mesa_10)
setor_rh.adicionar_mesa(mesa_11)


setor_juridico = Setor(3, "Jurídico")

mesa_12 = Mesa(12, "Contratos", "Simone Martins")
mesa_12.receber_processo("PROC-2026-0012")
mesa_12.receber_processo("PROC-2026-0013")
mesa_12.receber_processo("PROC-2026-0014")
mesa_12.receber_processo("PROC-2026-0015")

mesa_13 = Mesa(13, "Licitações", "André Rocha")
mesa_13.receber_processo("PROC-2026-0016")

mesa_14 = Mesa(14, "Convênios e Acordos", "Sidney Pena")
mesa_14.receber_processo("PROC-2026-0017")
mesa_14.receber_processo("PROC-2026-0018")

mesa_15 = Mesa(15, "Processos Judiciais", "Marcelo Silva")
mesa_15.receber_processo("PROC-2026-0019")

mesa_16 = Mesa(16, "Pareceres Jurídicos", "Monica Carvalho")
mesa_16.receber_processo("PROC-2026-0020")

setor_juridico.adicionar_mesa(mesa_12)
setor_juridico.adicionar_mesa(mesa_13)
setor_juridico.adicionar_mesa(mesa_14)
setor_juridico.adicionar_mesa(mesa_15)
setor_juridico.adicionar_mesa(mesa_16)


setor_compliance = Setor(4, "Compliance")

mesa_17 = Mesa(17, "Denúncias", "Kathyllin Souza")
mesa_17.receber_processo("PROC-2026-0021")
mesa_17.receber_processo("PROC-2026-0022")

mesa_18 = Mesa(18, "Conflito de Interesses", "Mayene Doria")
mesa_18.receber_processo("PROC-2026-0023")

mesa_19 = Mesa(19, "LGPD e Privacidade", "Cezar Augusto")
mesa_19.receber_processo("PROC-2026-0024")

mesa_20 = Mesa(20, "Anticorrupção", "Débora Christina")
mesa_20.receber_processo("PROC-2026-0025")

mesa_21 = Mesa(21, "Investigações Internas", "David Chen")
mesa_21.receber_processo("PROC-2026-0026")
mesa_21.receber_processo("PROC-2026-0027")

setor_compliance.adicionar_mesa(mesa_17)
setor_compliance.adicionar_mesa(mesa_18)
setor_compliance.adicionar_mesa(mesa_19)
setor_compliance.adicionar_mesa(mesa_20)
setor_compliance.adicionar_mesa(mesa_21)


setor_ti = Setor(5, "TI")

mesa_22 = Mesa(22, "Suporte Técnico", "Gabriel Oliveira")
mesa_22.receber_processo("PROC-2026-0028")

mesa_23 = Mesa(23, "Infraestrutura", "Rayane Santos")
mesa_23.receber_processo("PROC-2026-0029")

mesa_24 = Mesa(24, "Redes", "Stephanie Souza")
mesa_24.receber_processo("PROC-2026-0030")

mesa_25 = Mesa(25, "Banco de Dados", "Manuel Jacy")
mesa_25.receber_processo("PROC-2026-0031")
mesa_25.receber_processo("PROC-2026-0032")

mesa_26 = Mesa(26, "Equipamentos e Ativos", "Anatany Aparecida")
mesa_26.receber_processo("PROC-2026-0033")
mesa_26.receber_processo("PROC-2026-0034")
mesa_26.receber_processo("PROC-2026-0035")

mesa_27 = Mesa(27, "Segurança da Informação", "Guilherme Pinheiro")
mesa_27.receber_processo("PROC-2026-0036")

setor_ti.adicionar_mesa(mesa_22)
setor_ti.adicionar_mesa(mesa_23)
setor_ti.adicionar_mesa(mesa_24)
setor_ti.adicionar_mesa(mesa_25)
setor_ti.adicionar_mesa(mesa_26)
setor_ti.adicionar_mesa(mesa_27)


setor_sac = Setor(6, "SAC")

mesa_28 = Mesa(28, "Reclamações", "Mayumi Akira")
mesa_28.receber_processo("PROC-2026-0037")
mesa_28.receber_processo("PROC-2026-0038")
mesa_28.receber_processo("PROC-2026-0039")

mesa_29 = Mesa(28, "Cancelamentos", "José Bezerra")
mesa_29.receber_processo("PROC-2026-0040")
mesa_29.receber_processo("PROC-2026-0041")

mesa_30 = Mesa(28, "Retenção de Clientes", "Carlos Ferreira")
mesa_30.receber_processo("PROC-2026-0042")

mesa_31 = Mesa(28, "Trocas e Devoluções", "Cecílio Anselmo")
mesa_31.receber_processo("PROC-2026-0043")
mesa_31.receber_processo("PROC-2026-0044")

mesa_32 = Mesa(28, "Pós-Vendas", "Aliander Sant'ana")
mesa_32.receber_processo("PROC-2026-0045")
mesa_32.receber_processo("PROC-2026-0046")
mesa_32.receber_processo("PROC-2026-0047")
mesa_32.receber_processo("PROC-2026-0048")
mesa_32.receber_processo("PROC-2026-0049")

setor_sac.adicionar_mesa(mesa_28)
setor_sac.adicionar_mesa(mesa_29)
setor_sac.adicionar_mesa(mesa_30)
setor_sac.adicionar_mesa(mesa_31)
setor_sac.adicionar_mesa(mesa_32)




setor_juridico.listar_mesas()

mesa_16.listar_processos()

# Listagens
#setor_protocolo.listar_mesas()
#mesa_01.listar_documentos()
#mesa_02.listar_documentos()