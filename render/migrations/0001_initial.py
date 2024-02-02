# Generated by Django 5.0.1 on 2024-02-01 18:40

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ListaAtividades',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atividade', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Lista de Atividades',
                'verbose_name_plural': 'Admin | Lista de Atividades',
                'ordering': ('atividade',),
            },
        ),
        migrations.CreateModel(
            name='ListaIndicadoresMetricasTeletrabalho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('indicador', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Lista de Indicadores',
                'verbose_name_plural': 'Admin | Lista de Indicadores',
            },
        ),
        migrations.CreateModel(
            name='ListaPostosTrabalho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('setor', models.CharField(blank=True, max_length=255, null=True)),
                ('posto', models.CharField(max_length=255)),
                ('tipo', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Lista de Postos de Trabalho',
                'verbose_name_plural': 'Admin | Lista de Postos de Trabalho',
            },
        ),
        migrations.CreateModel(
            name='ListaSistemasTeletrabalho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sistema', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Lista de Sistemas',
                'verbose_name_plural': 'Admin | Lista de Sistemas',
                'ordering': ('sistema',),
            },
        ),
        migrations.CreateModel(
            name='ModelChangeLogsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField(blank=True, db_index=True)),
                ('table_name', models.CharField(blank=True, max_length=128)),
                ('table_row', models.CharField(blank=True, max_length=128)),
                ('action', models.CharField(blank=True, max_length=16)),
                ('old_value', models.CharField(blank=True, max_length=128, null=True)),
                ('new_value', models.CharField(blank=True, max_length=128, null=True)),
                ('timestamp', models.DateTimeField(blank=True)),
            ],
            options={
                'verbose_name': 'Logs autorizaçãos',
                'verbose_name_plural': 'Admin | Logs autorizações',
            },
        ),
        migrations.CreateModel(
            name='ModeloDocumento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_modelo', models.CharField(max_length=128)),
                ('descricao_modelo', models.TextField()),
                ('template_docx', models.FileField(upload_to='templates_docx/')),
            ],
            options={
                'verbose_name': 'Modelo docx',
                'verbose_name_plural': 'Admin | Modelos docx',
            },
        ),
        migrations.CreateModel(
            name='Numeracao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.IntegerField(default=2024, validators=[django.core.validators.MinValueValidator(2023)])),
                ('numero', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
            ],
            options={
                'verbose_name': 'Numeração',
                'verbose_name_plural': 'Admin | Numeração',
            },
        ),
        migrations.CreateModel(
            name='Setor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Setor',
                'verbose_name_plural': 'Admin | Setores',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Unidade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Unidade',
                'verbose_name_plural': 'Admin | Unidades',
            },
        ),
        migrations.CreateModel(
            name='ComissaoInterna',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('funcao', models.CharField(choices=[('presidente', 'Presidente'), ('membro', 'Membro')], max_length=128)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_cigt', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Comissão Interna',
                'verbose_name_plural': 'Admin | Comissão Interna',
            },
        ),
        migrations.CreateModel(
            name='DespachoEncaminhaAvaliacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('data_edicao', models.DateTimeField(auto_now=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('docx', models.FileField(blank=True, null=True, upload_to='generated_docx/')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='generated_pdf/')),
                ('ano', models.IntegerField(default=2024)),
                ('numeracao', models.IntegerField(blank=True, null=True)),
                ('ano_avaliacao', models.IntegerField(default=2024)),
                ('mes_avaliacao', models.IntegerField(default=2)),
                ('adicionado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_add_by', to=settings.AUTH_USER_MODEL)),
                ('membro_cigt', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_membro_cigt', to='render.comissaointerna')),
                ('modificado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_change_by', to=settings.AUTH_USER_MODEL)),
                ('modelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_modelo', to='render.modelodocumento')),
            ],
            options={
                'verbose_name': 'Despacho CIGT Encaminhamento Avaliação',
                'verbose_name_plural': 'Despachos CIGT | Encaminhamentos Avaliações',
            },
        ),
        migrations.CreateModel(
            name='AvaliacaoChefia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('data_edicao', models.DateTimeField(auto_now=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('docx', models.FileField(blank=True, null=True, upload_to='generated_docx/')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='generated_pdf/')),
                ('atestado_cumprimento_metas', models.CharField(choices=[('1', 'Atesto que o servidor cumpriu integralmente todas as metas e/ou condições o Plano de Trabalho'), ('2', 'Atesto que o servidor cumpriu as metas e/ou condições o Plano de Trabalho parcialmente'), ('3', 'Atesto que o servidor não cumpriu as metas e/ou condições o Plano de Trabalho')], max_length=255, null=True)),
                ('justificativa_nao_cumprimento', models.TextField(blank=True, null=True)),
                ('adicionado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_add_by', to=settings.AUTH_USER_MODEL)),
                ('modificado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_change_by', to=settings.AUTH_USER_MODEL)),
                ('encaminhamento_avaliacao_cigt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_encaminha_avaliacao', to='render.despachoencaminhaavaliacao')),
                ('modelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_modelo', to='render.modelodocumento')),
            ],
            options={
                'verbose_name': 'Avaliação da Chefia',
                'verbose_name_plural': 'Chefia | Avaliações da Chefia',
            },
        ),
        migrations.CreateModel(
            name='ManifestacaoInteresse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('data_edicao', models.DateTimeField(auto_now=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('docx', models.FileField(blank=True, null=True, upload_to='generated_docx/')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='generated_pdf/')),
                ('funcao', models.CharField(max_length=255, verbose_name='Função')),
                ('funcao_chefia', models.CharField(max_length=255, verbose_name='Função Chefia Imediata')),
                ('aprovado_chefia', models.CharField(blank=True, choices=[('aprovado', 'Aprovado'), ('reprovado', 'Reprovado')], max_length=16, null=True)),
                ('adicionado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_add_by', to=settings.AUTH_USER_MODEL)),
                ('chefia_imediata', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_chefia_imediata', to=settings.AUTH_USER_MODEL)),
                ('modificado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_change_by', to=settings.AUTH_USER_MODEL)),
                ('posto_trabalho', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_posto_trabalho_servidor', to='render.listapostostrabalho')),
                ('posto_trabalho_chefia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_posto_trabalho_chefia', to='render.listapostostrabalho')),
                ('servidor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_servidor', to=settings.AUTH_USER_MODEL)),
                ('modelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_modelo', to='render.modelodocumento')),
                ('setor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_setor', to='render.setor')),
                ('unidade', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_unidade', to='render.unidade')),
            ],
            options={
                'verbose_name': 'Manifestação de Interesse',
                'verbose_name_plural': 'Servidor | Manifestações de Interesse',
            },
        ),
        migrations.CreateModel(
            name='DespachoRetornoAvaliacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('data_edicao', models.DateTimeField(auto_now=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('docx', models.FileField(blank=True, null=True, upload_to='generated_docx/')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='generated_pdf/')),
                ('ano', models.IntegerField(default=2024)),
                ('numeracao', models.IntegerField(blank=True, null=True)),
                ('cumprimento_integral', models.CharField(choices=[('1', 'Servidor cumpriu integralmente todas as metas e/ou condições o Plano de Trabalho'), ('2', 'Servidor cumpriu as metas e/ou condições o Plano de Trabalho parcialmente'), ('3', 'Servidor não cumpriu as metas e/ou condições o Plano de Trabalho')], max_length=255, null=True)),
                ('adicionado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_add_by', to=settings.AUTH_USER_MODEL)),
                ('avaliacao_chefia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_avaliacao_chefia', to='render.avaliacaochefia')),
                ('membro_cigt', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_membro_cigt', to='render.comissaointerna')),
                ('modificado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_change_by', to=settings.AUTH_USER_MODEL)),
                ('modelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_modelo', to='render.modelodocumento')),
            ],
            options={
                'verbose_name': 'Despacho CIGT Retorno Avaliação',
                'verbose_name_plural': 'Despachos CIGT | Retorno Avaliações',
            },
        ),
        migrations.CreateModel(
            name='DespachoGenericoCIGT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('data_edicao', models.DateTimeField(auto_now=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('docx', models.FileField(blank=True, null=True, upload_to='generated_docx/')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='generated_pdf/')),
                ('ano', models.IntegerField(default=2024)),
                ('numeracao', models.IntegerField(blank=True, null=True)),
                ('interessada', models.CharField(max_length=255)),
                ('adicionado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_add_by', to=settings.AUTH_USER_MODEL)),
                ('membro_cigt', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_membro_cigt', to='render.comissaointerna')),
                ('modificado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_change_by', to=settings.AUTH_USER_MODEL)),
                ('modelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_modelo', to='render.modelodocumento')),
            ],
            options={
                'verbose_name': 'Despacho CIGT Generico',
                'verbose_name_plural': 'Despachos CIGT | Genéricos',
            },
        ),
        migrations.CreateModel(
            name='DeclaracaoNaoEnquadramentoVedacoes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('data_edicao', models.DateTimeField(auto_now=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('docx', models.FileField(blank=True, null=True, upload_to='generated_docx/')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='generated_pdf/')),
                ('estagio_probatorio', models.BooleanField(verbose_name='Não estou em estágio probatório')),
                ('cargo_chefia_direcao', models.BooleanField(verbose_name='Não ocupo cargo de chefia ou direção')),
                ('penalidade_disciplinar', models.BooleanField(verbose_name='Não sofri penalidade disciplinar nos últimos 12 meses')),
                ('justificativa_excecao', models.TextField(blank=True, null=True, verbose_name='Justificativa Exceções')),
                ('adicionado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_add_by', to=settings.AUTH_USER_MODEL)),
                ('modificado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_change_by', to=settings.AUTH_USER_MODEL)),
                ('manifestacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_interesse', to='render.manifestacaointeresse')),
                ('modelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_modelo', to='render.modelodocumento')),
            ],
            options={
                'verbose_name': 'Declaração Não Enquadramento Vedações',
                'verbose_name_plural': 'Servidor | Declarações Não Enquadramento Vedações',
            },
        ),
        migrations.CreateModel(
            name='AutorizacoesExcecoes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('docx', models.FileField(blank=True, null=True, upload_to='generated_docx/')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='generated_pdf/')),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_edicao', models.DateTimeField(auto_now=True)),
                ('aprovado_gabinete', models.CharField(blank=True, choices=[('aprovado', 'Aprovado'), ('reprovado', 'Reprovado')], max_length=16, null=True)),
                ('modificado_por', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_user_aprovacao', to=settings.AUTH_USER_MODEL)),
                ('declaracao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_declaracao', to='render.declaracaonaoenquadramentovedacoes')),
                ('modelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_modelo', to='render.modelodocumento')),
            ],
            options={
                'verbose_name': 'Autorização Exceção Teletrabalho Chefia',
                'verbose_name_plural': 'Direção | Autorizações Exceções Teletrabalho Chefias',
            },
        ),
        migrations.CreateModel(
            name='ParecerCIGT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('data_edicao', models.DateTimeField(auto_now=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('docx', models.FileField(blank=True, null=True, upload_to='generated_docx/')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='generated_pdf/')),
                ('ano', models.IntegerField(default=2024)),
                ('numeracao', models.IntegerField(blank=True, null=True)),
                ('deferido', models.BooleanField(default=True)),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('adicionado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_add_by', to=settings.AUTH_USER_MODEL)),
                ('membro_cigt', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_membro_cigt', to='render.comissaointerna')),
                ('modelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_modelo', to='render.modelodocumento')),
                ('modificado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_change_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Despacho CIGT Plano de Trabalho',
                'verbose_name_plural': 'Despachos CIGT | Plano de Trabalho',
                'ordering': ('id',),
            },
        ),
        migrations.AddField(
            model_name='despachoencaminhaavaliacao',
            name='despacho_cigt',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_despacho_cigt', to='render.parecercigt'),
        ),
        migrations.CreateModel(
            name='PlanoTrabalho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('data_edicao', models.DateTimeField(auto_now=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('docx', models.FileField(blank=True, null=True, upload_to='generated_docx/')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='generated_pdf/')),
                ('periodo_comparecimento', models.CharField(max_length=255, null=True)),
                ('periodo_acionamento', models.CharField(max_length=255, null=True)),
                ('aprovado_chefia', models.CharField(blank=True, choices=[('aprovado', 'Aprovado'), ('reprovado', 'Reprovado')], max_length=16, null=True)),
                ('aprovado_cigt', models.CharField(blank=True, choices=[('aprovado', 'Aprovado'), ('reprovado', 'Reprovado')], max_length=16, null=True)),
                ('adicionado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_add_by', to=settings.AUTH_USER_MODEL)),
                ('manifestacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_interesse', to='render.manifestacaointeresse')),
                ('modelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_modelo', to='render.modelodocumento')),
                ('modificado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_change_by', to=settings.AUTH_USER_MODEL)),
                ('sistemas', models.ManyToManyField(to='render.listasistemasteletrabalho')),
                ('usuario_chefia_aprovacao', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_user_chefia_aprovacao', to=settings.AUTH_USER_MODEL)),
                ('usuario_cigt_aprovacao', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_user_cigt_aprovacao', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Plano de Trabalho',
                'verbose_name_plural': 'Chefia | Planos de Trabalho',
            },
        ),
        migrations.CreateModel(
            name='PeriodoTeletrabalho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_inicio', models.DateField(blank=True, null=True)),
                ('data_fim', models.DateField(blank=True, null=True)),
                ('plano_trabalho', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_plano_trabalho', to='render.planotrabalho')),
            ],
            options={
                'verbose_name': 'Período Teletrabalho',
                'verbose_name_plural': 'Admin | Períodos Teletrabalho',
            },
        ),
        migrations.AddField(
            model_name='parecercigt',
            name='plano_trabalho',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_plano_trabalho', to='render.planotrabalho'),
        ),
        migrations.CreateModel(
            name='AtividadesTeletrabalho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_qualitativa', models.CharField(blank=True, default='---', max_length=255, null=True)),
                ('meta_quantitativa', models.CharField(max_length=255)),
                ('atividade', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_atividade', to='render.listaatividades')),
                ('tipo_meta_quantitativa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_metrica', to='render.listaindicadoresmetricasteletrabalho')),
                ('plano_trabalho', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_plano_trabalho', to='render.planotrabalho')),
            ],
            options={
                'verbose_name': 'Atividade Teletrabalho',
                'verbose_name_plural': 'Chefia | Atividades do Plano de Trabalho',
            },
        ),
        migrations.CreateModel(
            name='PortariasPublicadasDOE',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('data_edicao', models.DateTimeField(auto_now=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('docx', models.FileField(blank=True, null=True, upload_to='generated_docx/')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='generated_pdf/')),
                ('ano', models.IntegerField(blank=True, null=True)),
                ('numero', models.IntegerField(blank=True, null=True)),
                ('data_publicacao', models.DateField(blank=True, null=True)),
                ('has_inclusoes', models.BooleanField()),
                ('has_exclusoes', models.BooleanField()),
                ('modelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_modelo', to='render.modelodocumento')),
            ],
            options={
                'verbose_name': 'CIGT | Portarias REPR DOE',
                'verbose_name_plural': 'CIGT | Portarias REPR DOE',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='ProtocoloAutorizacaoTeletrabalho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('data_edicao', models.DateTimeField(auto_now=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('docx', models.FileField(blank=True, null=True, upload_to='generated_docx/')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='generated_pdf/')),
                ('sid', models.CharField(blank=True, max_length=12, null=True)),
                ('publicado_doe', models.CharField(blank=True, choices=[('nao_publicado', 'Aguardando Publicação'), ('publicado', 'Publicado'), ('republicado', 'Republicado')], max_length=16, null=True)),
                ('adicionado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_add_by', to=settings.AUTH_USER_MODEL)),
                ('despacho_cigt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_despacho_cigt', to='render.parecercigt')),
                ('modelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_modelo', to='render.modelodocumento')),
                ('modificado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_change_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Protocolo Autorização Teletrabalho',
                'verbose_name_plural': 'Chefias | Protocolos de Autorização Teletrabalho',
                'ordering': ('sid',),
            },
        ),
        migrations.CreateModel(
            name='ControleMensalTeletrabalho',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('competencia', models.DateField()),
                ('vigente', models.BooleanField()),
                ('publicado_doe', models.CharField(choices=[('nao_publicado', 'Aguardando Publicação'), ('publicado', 'Publicado'), ('republicado', 'Republicado')], default='nao_publicado', max_length=16)),
                ('protocolo_alteracao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_protocolo_alteracao', to='render.protocoloautorizacaoteletrabalho')),
                ('protocolo_autorizacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_protocolo_autorizacao', to='render.protocoloautorizacaoteletrabalho')),
            ],
            options={
                'verbose_name': 'CIGT | Controle Mensal Teletrabalho',
                'verbose_name_plural': 'CIGT | Controle Mensal Teletrabalho',
            },
        ),
        migrations.AddField(
            model_name='modelodocumento',
            name='setor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_setor', to='render.setor'),
        ),
        migrations.CreateModel(
            name='DespachoArquivamentoManifestacaoCIGT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=django.utils.timezone.now)),
                ('data_edicao', models.DateTimeField(auto_now=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('docx', models.FileField(blank=True, null=True, upload_to='generated_docx/')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='generated_pdf/')),
                ('ano', models.IntegerField(default=2024)),
                ('numeracao', models.IntegerField(blank=True, null=True)),
                ('sid', models.CharField(max_length=12)),
                ('adicionado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_add_by', to=settings.AUTH_USER_MODEL)),
                ('membro_cigt', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_membro_cigt', to='render.comissaointerna')),
                ('modificado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_change_by', to=settings.AUTH_USER_MODEL)),
                ('modelo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_modelo', to='render.modelodocumento')),
                ('unidade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_unidade', to='render.unidade')),
            ],
            options={
                'verbose_name': 'Despacho CIGT Arquivamento Manifestação',
                'verbose_name_plural': 'Despachos CIGT | Arquivamento Manifestações',
            },
        ),
    ]
