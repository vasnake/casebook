# -*- mode: text; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

################################################################################

Письмо 1

Есть некая система – http://casebook.ru
Там содержится информация по всяким юридическим делам.
Мы можем раз в день читать автоматом оттуда данные и складывать в базу?

################################################################################

Письмо 2

Примерный сценарий пользователя на сайте
Со слов адвоката, типичный запрос выглядит так…
Вводим в поле Поиск название организации,
выбираем дело
и переходим к кому-то из участников.
Тут нужны все поля. Потестироваться можно на названии и реквизитах – ИНН, КПП и пр. ОГРН.
Отсюда почти всегда качают выписку из ЕГРЮЛ (ссылка в левом верхнем углу) и очень часто
используется кнопка Запрос данных (в разделе История изменений руководителя),
но после нажатия кнопки всплывает оповещение «Документация будет подготовлена в течение 15 минут. О готовности мы сообщим по электронной почте.», через некоторое время в почту падает не оповещение, а ответ примерно такого вида:
...
Дальше остальные пункты верхнего меню:
Отчётность (нужна реже, но целиком),
Арбитражные дела и
Дела СОЮ (как правило дальнейший поиск по участникам как уже описанный).

################################################################################

Письмо 3

Заходим в Casebook под имеющейся учёткой, в поле Поиск вводим газпром,
в предложенном списке вариантов дважды
кликаем на
OAO «ГАЗПРОМБАНК»
видим выдачу из 66 строк. Это остальные участники всех судебных процессов с участием OAO «ГАЗПРОМБАНК».
Можно ткнуть в название участника и получить по нему судебную статистику,
можно в любой другой столбец в строке – прямо в списке раскроется карточка участника со списком дел.
В верхнем меню кликаем Арбитражные дела – видим список соответствующих дел с участием нашего фигуранта.
Аналогично Дела СОЮ – дела судов общей юрисдикции.
По клику на номере дела откроется описание дела с возможностью скачать документы по делу, находящиеся в общем доступе.
В списке Участники ниже поля Поиск можем уточнить – ищем ли мы все дела с участием OAO «ГАЗПРОМБАНК»,
или только где он выступает в конкретной роли (истец, ответчик и т.п.).
Кликом по любой фамилии (ИНН, названию организации и т.п.), являющейся ссылкой, можно получить информацию по соответствующему персонажу и т.п.
В качестве затравки для поиска можно использовать название любой известной компании или банка, любую распространённую фамилию.
В выдаче по ним можно взять для примера номера дел.
Наши юристы чаще всего ищут документы (решения и определения судов) и информацию о сроках заседаний, обжалований, ушло ли дело на апелляцию и т.п.

################################################################################

Письмо 4

Задача - исходя из поиска по заданным параметрам собрать ВСЮ имеющуюся в Кейсбуке информацию.

1.       Поиск по делам:
Как пример, интересны следующие дела:
    - № А40-51217/2011
    - № А65-27211/2011
    - № А40-27010/2012

2.       Поиск по лицам:
    а) по юридическим лицам (компаниям)
    - ОАО «ЛУКОЙЛ-Коми» (ИНН 1106014140 )
    - компания «Демесне Инвестментс Лимитед»
(здесь возникает один интересный вопрос; дело в том, что у иностранных компаний нет ни ИНН, ни ОГРН; можно попробовать в таких случаях помимо наименования добавлять адрес, но не уверен, что это может помочь; в общем, написал Вам иностранную компанию в качестве «интересного случая» для проверки правильности работы программы; посмотрите как программа будет работать с такими запросами и тогда сможем понимать как с этим жить (мое скромное мнение)(или же давайте как-то это обсудим));
    - ОАО «Глобинторг» (ИНН 7723830905)

    б) по физическим лицам
    - Волков Валерий Юрьевич
    - Габдрахимов Александр Мухаматшевич
    - Шейдорова Александра Витальевна

################################################################################

Поисковые запросы и результаты, обзор

Похоже, поиск проводится тремя запросами: suggest, cases, sides.
Запросы выдаются одновременно и отображение начинается после отработки последнего.
suggest нужен только для подсказок в поле ввода.
Реально поиск проводится по cases, sides. (http://casebook.ru/api/Search/Cases, http://casebook.ru/api/Search/Sides)
Выдача результата в браузер идет в зависимости от того, что найдено - если дел не найдено, выводятся стороны.

Результаты выдаются в виде иерархических объектов в виде текста JSON.
Объекты могут различаться по составу, но часто можно выделить общие свойства.
Если свойство присутствует, его значение может быть как пустой строкой, так и null, помимо ожидаемого значения.

Соответственно, в качестве результата поиска мы получаем (вынесем разные ошибки за скобки) две коллекции:
 - список дел (cases)
 - список сторон (sides)

Каждое дело характеризуется такими основными параметрами:
    номер
    дата
    судья
    суд
    разный описательный текст
    тип дела
    сумма денег
    список инстанций (судов)
    список сторон
    последнее событие
    следующее (ожидаемое) событие

Тут (в списках) выделяются связанные сущности: инстанция (суд), сторона (участник), событие

В связи с делом каждая инстанция (суд) характеризуется (основные параметры):
    название инстанции
    судья
    уровень инстанции
    даты входа-выхода дела

Участник:
    тип
    название
    ИНН, ОГРН, ОКПО
    адрес
    ФИО начальника
    признак физ.лица

Событие:
    дата
    описание
    суть события (список вопросов)
    тип события
    ссылка на документ
    суд
    судья
    номер инстанции?
    заявитель

Итого, можно выделить такие сущности:
    дело
    суд (инстанция)
    судья
    сторона (участник)
    физ.лицо (в том числе как сторона и как начальник и как самостоятельное физ.лицо)
    событие
    документ

Между собой эти сущности могут быть связаны:
    дело проходит по разным инстанциям
    в деле участвуют разные стороны
    по делу происходят разные события
    дело рассматривается судьей, в суде
    в инстанции дело рассматривается судьей, в суде
    у участника может быть начальник - физ.лицо
    по событию может быть документ
    событие назначено в инстанцию, для судьи
    событие подано заявителем - участником

################################################################################

Поиск дел - POST http://casebook.ru/api/Search/Cases

Тело запроса "payload" передается в виде текста JSON -
{"StatusEx":[],"SideTypes":[],"ConsiderType":-1,"CourtType":-1,"CaseNumber":null,"CaseCategoryId":"","MonitoredStatus":-1,"Courts":[],"Instances":[],"Judges":[],"Delegate":"","StateOrganizations":[],"DateFrom":null,"DateTo":null,"SessionFrom":null,"SessionTo":null,"FinalDocFrom":null,"FinalDocTo":null,"MinSum":0,"MaxSum":-1,"Sides":[],"CoSides":[],"Accuracy":2,"Page":1,"Count":30,"OrderBy":"incoming_date_ts desc","JudgesNames":[],"Query":"№ А40-51217/2011"}
В котором главынй параметр поиска - "Query":"№ А40-51217/2011"

Ответ приходит как обьект JSON
{
  "Message": "",
  "ServerDate": "2014-03-21T13:59:41.0008466+04:00",
  "Success": true,
  "Timings": [
    "GetCasesIdsFormSpx 00:00:00.6140000",
    "GetCasesList.Sql 00:00:00.2880000",
    "GetCaseBankruptStages 00:00:00.0400000",
    "GetCasesList.SortAndMerge 00:00:00",
    "Warnings:"
  ]
  "Result": {объект развернут ниже}
}

В ответе нужно поинтересоваться следующими параметрами:
resp.Success - if false - error, что значит - сбой авторизации, сервера или еще чего. Сообщение о неприятностях надо брать в
resp.Message - если все в порядке, то сообщение пустое. Если сообщение есть, то была ошибка или есть предупреждение
    в любом случае непустого сообщения, данные результата недостоверны.
resp.Timings - может быть null или массив строк, применяется при отладке и содержит значения задержек или сообщения о обломе отдельных агентов.
resp.Result - обьект с данными ответа, может быть пустой:

  "Result": {
    "MaxSum": -1.0,
    "FoundSideIdByCaseId": {
      "6a85b808-24f6-4ddb-ae53-60ffde4cbca0": 1878762
    },
    "Page": 1,
    "PageSize": 30,
    "TotalCount": 1,
    "PagesCount": 1,
    "Items": [массив развернут ниже]
  }

В данных содержится такая информация:
resp.Result.FoundSideIdByCaseId - словарь (список имя-значение), может быть пустой.
    Имя это CaseId, идентификатор дела; значение это FakeId в списке сторон Sides.
    Зачем это нужно - пока не ясно, ибо по каждому делу сторон много, тогда как в этом списке - одна сторона на одно дело.
resp.Result.TotalCount - число найденных по запросу дел.
resp.Result.Items - список найденных дел, может быть пустой:

    "Items": [
      {
        "CaseId": "6a85b808-24f6-4ddb-ae53-60ffde4cbca0",
        "FoundInstanceId": "00000000-0000-0000-0000-000000000000",
        "CaseNumber": "А40-51217/2011",
        "StartDate": "2011-08-30T00:00:00",
        "JudgeId": "4ff54bc1-4f40-426a-aa70-63c1fdf5e0a9",
        "Judge": "Сабирова М. Ф.",
        "Court": "АС города Москвы",
        "BankruptStage": "Конкурсное производство",
        "Status": "Рассматривается в апелляционной, первой, надзорной и кассационной инстанциях",
        "CaseTypeMCode": "Б",
        "CaseCategory": "О несостоятельности (банкротстве)",
        "CaseType": "о несостоятельности (банкротстве) организаций и граждан",
        "ClaimSum": 16355838800.99,
        "RecoverySum": 16355838800.99,
        "Comment": "",
        "IsMonitored": false,
        "InFolders": [],
        "IsFavorite": false,
        "UpdatesCount": 0,
        "IsGJ": false,
        "IsSimpleJustice": false,
        "Instances": [see explanation later],
        "Sides": [see explanation later],
        "LastEvents": [see explanation later],
        "NextEvent": {see explanation later}
      }
    ]

Внутри каждого найденного дела могут быть интересны следующие данные:
resp.Result.Items[i].CaseId - системный идентификатор дела
resp.Result.Items[i].CaseNumber - официальный номер дела
resp.Result.Items[i].StartDate - начальная дата рассмотрения дела? Юристы знают
resp.Result.Items[i].JudgeId - системный идентификатор судьи
resp.Result.Items[i].Judge - фамилия И.О. судьи
resp.Result.Items[i].Court - название суда
resp.Result.Items[i].BankruptStage - что-то из юр.терминологии про судопроизводство. Пока попадалось только "Конкурсное производство". Юристы знают.
resp.Result.Items[i].Status - текст про состояние дела?
resp.Result.Items[i].CaseTypeMCode - понятия не имею, что обозначет литера "Б" - код типа дела?
resp.Result.Items[i].CaseCategory - название категории дела, (о банкротстве)
resp.Result.Items[i].CaseType - название типа дела (о несостоятельности ...)
resp.Result.Items[i].ClaimSum - затребованная сумма в рублях?
resp.Result.Items[i].RecoverySum - сумма покрытия?
resp.Result.Items[i].Comment - комментарий? Пока попадался только пустой
resp.Result.Items[i].Instances - список инстанций (судов) по которым дело проходит. Подробности ниже
resp.Result.Items[i].Sides - список участвующих сторон, часто длинный. Подробности ниже
resp.Result.Items[i].LastEvents - список последних событий. Подробности ниже
resp.Result.Items[i].NextEvent - null или обьект - следующее запланированное событие. Подробности ниже

resp.Result.Items[i].Instances - список инстанций (судов) по которым дело проходит:

        "Instances": [
          {
            "Court": "АС города Москвы",
            "Judge": "Мироненко Э. В.",
            "CourtTag": "MSK",
            "InstanceLevel": 1,
            "FinishState": 0,
            "FinishDate": "2013-07-15T00:00:00",
            "IncomingDate": "2013-06-19T00:00:00",
            "JudgeId": "d615e644-c551-4d91-877e-72a455e81c2f"
          },
...
          {
            "Court": "ФАС МО",
            "Judge": "Бусарова Л. В.",
            "CourtTag": "FASMO",
            "InstanceLevel": 3,
            "FinishState": 0,
            "FinishDate": null,
            "IncomingDate": "2014-03-06T00:00:00",
            "JudgeId": "df5a5360-e6f0-452c-b057-65744df02307"
          }
        ]

resp.Result.Items[i].Instances[j].Court - название суда
resp.Result.Items[i].Instances[j].Judge - фамилия И.О. судьи
resp.Result.Items[i].Instances[j].CourtTag - территориальная принадлежность суда, что-то типа метки
resp.Result.Items[i].Instances[j].InstanceLevel - уровень инстанции, число
resp.Result.Items[i].Instances[j].FinishState - пока попадались только нули. Конечная инстанция?
resp.Result.Items[i].Instances[j].FinishDate - null или дата завершения рассмотрения дела в этой инстанции?
resp.Result.Items[i].Instances[j].IncomingDate - дата начала рассмотрения дела?
resp.Result.Items[i].Instances[j].JudgeId - системный идентификатор судьи

resp.Result.Items[i].Sides - список участвующих сторон, часто длинный:

        "Sides": [
          {
            "Type": 0,
            "FakeId": 3587005,
            "TypeName": "Истец",
            "OrganizationId": 0,
            "ShortName": "АНГЛО АЙРИШ БЭНК КОРПОРЭЙШН ЛИМИТЕД",
            "Name": "АНГЛО АЙРИШ БЭНК КОРПОРЭЙШН ЛИМИТЕД",
            "IsBranch": false,
            "IsUnique": false,
            "IsNotPrecise": false,
            "Inn": null,
            "Ogrn": null,
            "Okpo": null,
            "Address": "123317, Россия, Москва, Преснеская наб., д. 10 Башня на набережной, Блок В, эт. 17 ЮФ Меджистерс",
            "Region": null,
            "OrgForm": null,
            "HeadFio": null,
            "StorageId": null,
            "HidePersonalData": 0,
            "IsPhysical": false,
            "IsMonitored": false,
            "InFolders": null
          },
...
          {
            "Type": 1,
            "FakeId": 1878768,
            "TypeName": "Ответчик",
            "OrganizationId": 0,
            "ShortName": "ООО \"Компания \"Финансстройинвестмент\"",
            "Name": "ООО \"Компания \"Финансстройинвестмент\"",
            "IsBranch": false,
            "IsUnique": false,
            "IsNotPrecise": false,
            "Inn": "7717532844",
            "Ogrn": null,
            "Okpo": null,
            "Address": "107113, Россия, Москва, Сокольническая пл., д. 4А",
            "Region": null,
            "OrgForm": null,
            "HeadFio": null,
            "StorageId": null,
            "HidePersonalData": 0,
            "IsPhysical": false,
            "IsMonitored": false,
            "InFolders": null
          }
        ]

resp.Result.Items[i].Sides[j].Type - число, тип стороны (1 - ответчик, 0 - истец, и т.д.)
resp.Result.Items[i].Sides[j].FakeId - численный псевдо идентификатор стороны, может упоминаться в resp.Result.FoundSideIdByCaseId
resp.Result.Items[i].Sides[j].TypeName - название типа стороны (ответчик, истец, и т.д.)
resp.Result.Items[i].Sides[j].OrganizationId - пока попадались только нули
resp.Result.Items[i].Sides[j].ShortName - краткое название стороны
resp.Result.Items[i].Sides[j].Name - название стороны
resp.Result.Items[i].Sides[j].IsBranch - является ли филиалом?
resp.Result.Items[i].Sides[j].IsUnique - пока попадались только false
resp.Result.Items[i].Sides[j].IsNotPrecise - пока попадались только false
resp.Result.Items[i].Sides[j].Inn - ИНН стороны или пустая строка
resp.Result.Items[i].Sides[j].Ogrn - ОГРН, или null или пустая строка
resp.Result.Items[i].Sides[j].Okpo - ОКПО, или null или пустая строка
resp.Result.Items[i].Sides[j].Address - почтовый адрес стороны
resp.Result.Items[i].Sides[j].Region - название территориального региона
resp.Result.Items[i].Sides[j].OrgForm - название организационной формы? Почти всегда null
resp.Result.Items[i].Sides[j].HeadFio - ФИО начальника, почти всегда null
resp.Result.Items[i].Sides[j].StorageId - пока попадались только null
resp.Result.Items[i].Sides[j].HidePersonalData - флажок сокрытия персональных данных (0, 1, null)
resp.Result.Items[i].Sides[j].IsPhysical - является ли сторона физлицом? (true, false)
resp.Result.Items[i].Sides[j].IsMonitored - пока попадались только false
resp.Result.Items[i].Sides[j].InFolders - пока попадались только null и [] - пустой список

resp.Result.Items[i].LastEvents - список последних событий:

        "LastEvents": [
          {
            "Date": "2014-03-20T00:00:00",
            "Description": null,
            "ContentTypes": [
              "Об ознакомлении с материалами дела (ст. 41 АПК)"
            ],
            "DecisionType": "",
            "DocumentId": "2b23b931-9b0b-4926-8483-240ce0393e00",
            "Court": "9 ААС",
            "Judge": null,
            "JudgeId": "00000000-0000-0000-0000-000000000000",
            "Declarer": "ООО \"Компания \"Финансстройинвестмент\"",
            "DeclarerInfo": null,
            "InstanceNumber": "09АП-7189/2014",
            "NeedJudges": false,
            "TypeName": "Ходатайства",
            "DocumentFileName": null
          }
        ]

resp.Result.Items[i].LastEvents[j].Date - дата события
resp.Result.Items[i].LastEvents[j].Description - описание события
resp.Result.Items[i].LastEvents[j].ContentTypes - список вопросов, повестка заседания?
resp.Result.Items[i].LastEvents[j].DecisionType - пока попадались только пустые
resp.Result.Items[i].LastEvents[j].DocumentId - системный идентификатор документа
resp.Result.Items[i].LastEvents[j].Court - название суда
resp.Result.Items[i].LastEvents[j].Judge - фамилия И.О. судьи
resp.Result.Items[i].LastEvents[j].JudgeId - системный идентификатор судьи
resp.Result.Items[i].LastEvents[j].Declarer - название заявителя
resp.Result.Items[i].LastEvents[j].DeclarerInfo - пока попадались только null
resp.Result.Items[i].LastEvents[j].InstanceNumber - номер инстанции? Больше похоже на номер дела
resp.Result.Items[i].LastEvents[j].NeedJudges - нужен ли судья? (true, false)
resp.Result.Items[i].LastEvents[j].TypeName - название типа события
resp.Result.Items[i].LastEvents[j].DocumentFileName - пока попадались только null

resp.Result.Items[i].NextEvent - null или обьект - следующее запланированное событие:

        "NextEvent": {
          "Date": "2014-03-24T12:00:00",
          "Description": "Судебное заседание\n9 ААС, 10 (кабинет 204)",
          "ContentTypes": null,
          "DecisionType": null,
          "DocumentId": "b22e085c-d093-41e7-9680-1ffe19698967",
          "Court": "9 ААС",
          "Judge": null,
          "JudgeId": "00000000-0000-0000-0000-000000000000",
          "Declarer": null,
          "DeclarerInfo": null,
          "InstanceNumber": "09АП-7189/2014",
          "NeedJudges": false,
          "TypeName": null,
          "DocumentFileName": null
        }

resp.Result.Items[i].NextEvent.Date ... см. описание resp.Result.Items[i].LastEvents[j].Date
остальные поля тоже идентичны resp.Result.Items[i].LastEvents[j].*

################################################################################

Примеры поисковых запросов

Поиск по делам

{{{
№ А40-51217/2011
    запрос/ответ (3) в файле
        data/query.case01.json
    Отображается в браузере как:
        data/casebook.case01.result01.png

№ А65-27211/2011
    запрос/ответ (3, cases - Warnings - datasource timeout) в файле
        data/query.case02.json
    Отображается в браузере как:
        data/casebook.case02.result01.png

№ А40-27010/2012
    запрос/ответ в файле
        data/query.case03.json
    Отображается в браузере как:
        data/casebook.case03.result01.png
}}}


Поиск по юридическим лицам (компаниям)

{{{
ОАО «ЛУКОЙЛ-Коми» (ИНН 1106014140 )
    запрос/ответ (3, cases - Warnings) в файле
        data/query.company01.json
    Отображается в браузере как:
        data/casebook.company01.result01.png

компания «Демесне Инвестментс Лимитед»
    запрос/ответ (3, cases - Warnings) в файле
        data/query.company02.json
    Отображается в браузере как:
        data/casebook.company02.result01.png

ОАО «Глобинторг» (ИНН 7723830905)
    это очень интересный вариант - поиск по делам ничего не находит, но находит поиск по сторонам (sides)
    запрос/ответ (3) в файле
        data/query.company03.json
    Отображается в браузере как:
        data/casebook.company03.result01.png
}}}


Поиск по физическим лицам

{{{
Волков Валерий Юрьевич
    запрос/ответ (3, cases - Warnings) в файле
        data/query.person01.json
    Отображается в браузере как:
        data/casebook.person01.result01.png

Габдрахимов Александр Мухаматшевич
    тоже ничего не находит. четко видно как выполняется три запроса: suggest, cases, sides
    запрос/ответ (3) в файле
        data/query.person02.json
    Отображается в браузере как:
        data/casebook.person02.result01.png

Шейдорова Александра Витальевна
    запрос/ответ (3) в файле
        data/query.person03.json
    Отображается в браузере как:
        data/casebook.person03.result01.png
}}}

################################################################################

Возможно получение таких сообщений, данных либо нет вообще, либо данные не все

HTTP/1.0 200 OK
Cache-Control: no-cache
Pragma: no-cache
Content-Length: 547
Content-Type: application/json; charset=utf-8
Expires: -1
Server: Microsoft-IIS/7.5
X-AspNet-Version: 4.0.30319
X-Powered-By: ASP.NET
X-Powered-By: ARR/2.5
X-Powered-By: ASP.NET
Date: Thu, 20 Mar 2014 16:50:59 GMT
X-Cache: MISS from gate.algis.com
X-Cache-Lookup: MISS from gate.algis.com:3128
Via: 1.1 gate.algis.com:3128 (squid/2.7.STABLE9)
Connection: keep-alive
Proxy-Connection: keep-alive

{
  "Message": "Результаты собраны не из всех источников. Повторите запрос позже для уточнения",
  "ServerDate": "2014-03-20T20:50:59.0003827+04:00",
  "Result": {
    "MaxSum": -1.0,
    "FoundSideIdByCaseId": {},
    "Page": 1,
    "PageSize": 30,
    "TotalCount": 0,
    "PagesCount": 0,
    "Items": []
  },
  "Success": true,
  "Timings": [
    "GetCasesIdsFormSpx 00:00:03.0700000",
    "Warnings:index ix_sides: agent cg-sps11:3327: query timed out"
  ]
}

################################################################################
