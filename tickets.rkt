;;; Binding cutting task calculator.
;;; Require this in your tasks file with
;;;
;;; (require "booky.rkt")

#lang racket

(provide (all-defined-out)) 

(define left-margin (make-parameter 2))
(define right-margin (make-parameter 2))
(define upper-margin (make-parameter 5))
(define lower-margin (make-parameter 5))
(define font-size (make-parameter 11))
(define vertical-stretch (make-parameter 1.2))
(define title-width (make-parameter 26))
(define title-styling (make-parameter "\\large"))
(define label-width (make-parameter 18))
(define volume-separation (make-parameter 0))
(define ticket-spacing (make-parameter 4))

(define cardboard-label (make-parameter "carton"))
(define paper-label (make-parameter "papier"))
(define buckram-label (make-parameter "buckram"))
(define backcard-label (make-parameter "carte-a-dos"))

(struct volume (edition backcard-width) #:prefab)
(struct ticket (title color volume-data-list) #:prefab)
(struct volume-data (edition
                     cardboard-height
                     cardboard-width
                     paper-height
                     paper-width
                     buckram-height
                     buckram-width
                     backcard-height
                     backcard-width) #:prefab)

(define (ticket-maker title cover-height cover-width color volume-list)
  (ticket title
          color
          (map (lambda (v)
                 (match v
                   ((volume edition backcard-width)
                    (volume-data edition ;; edition
                                 cover-height ;; cardboard-height
                                 cover-width  ;; cardboard-width
                                 (+ 30 cover-height) ;; paper-height
                                 (+ backcard-width
                                    50
                                    (* 2 cover-width))  ;; paper-width 
                                 (+ 40 cover-height)    ;; buckram-height
                                 (+ 100 backcard-width) ;; buckram-width
                                 cover-height           ;; backcard-height
                                 backcard-width         ;; backcard-width
                                 ))))
               volume-list)))

(define (doc-setup body)
  (string-append
   (format "\\documentclass[~apt,a4paper]{memoir}\n"
           (font-size))
   (format "\\setlrmarginsandblock{~amm}{~amm}{*}\n"
           (left-margin)
           (right-margin))
   (format "\\setulmarginsandblock{~amm}{~amm}{*}\n"
           (upper-margin)
           (lower-margin))
   "\\fixthelayout\n"
   "\\renewcommand{\\familydefault}{\\sfdefault}\n"
   "\\usepackage{multirow}\n\n"
   "\\begin{document}\n\n"
   body
   "\n\n\\vfill\n\\end{document}\n"))

(define (table-setup column-args body)
  (string-append
   (format "{\\renewcommand{\\arraystretch}{~a}\n" (vertical-stretch))
   (format "\\begin{tabular}{~a}\n" column-args)
   "\\hline\n"
   body
   "\\hline\n\\end{tabular}}\n"))

(define (column-args number-of-volumes)
  (string-append (format "|c|p{~amm}|" (label-width))
                 (apply string-append
                        (make-list (- number-of-volumes 1)
                                   (format  "c|c|p{~amm}|"
                                            (volume-separation))))
                 "c|c|"))

(define (header-row title color volumes)
  (string-append
   (format "\\multirow{6}{~amm}{~a ~a}"
           (title-width)
           (title-styling)
           title)
   (string-append
    (format "& \\multirow{2}{*}{\\Large ~a} &" color)
    (string-join
     (map (lambda (v)
            (format "\\multicolumn{2}{c|}{~a}"
                    (volume-data-edition v)))
          volumes)
     " & & ")
   " \\\\\n")))

(define (subheader-row number-of-volumes)
  (string-append
   (apply string-append
          (for/list ((n number-of-volumes))
            (format "\\cline{~a-~a}" (* 3 (+ n 1)) (+ 1 (* 3 (+ n 1))))))
   "\n"
   (apply string-append (make-list number-of-volumes " & & H & W"))
   "\\\\\n"))

(define (data-cline number-of-volumes)
  (string-append
   "\\cline{2-2}"
   (apply string-append
          (for/list ((n number-of-volumes))
            (format "\\cline{~a-~a}"
                    (* 3 (+ n 1))
                    (+ 1 (* 3 (+ n 1))))))
   "\n"))

(define (data-row-maker data-label height-accessor width-accessor)
  (define (format-pair format-string v)
    (format format-string
            (height-accessor v)
            (width-accessor v)))
  (lambda (volumes)
    (let loop ((vs volumes) (result (format "& ~a " data-label)))
      (cond ((empty? vs)
             (string-append result " \\\\\n"))
            ((empty? (cdr vs))
             (loop (cdr vs)
                   (string-append result
                                  (format-pair " & ~a & ~a" (car vs)))))
            (else
             (loop (cdr vs)
                   (string-append result
                                  (format-pair " & ~a & ~a &" (car vs)))))))))

(define cardboard-row
  (data-row-maker (cardboard-label)
                  volume-data-cardboard-height
                  volume-data-cardboard-width))

(define paper-row
  (data-row-maker (paper-label)
                  volume-data-paper-height
                  volume-data-paper-width))

(define buckram-row
  (data-row-maker (buckram-label)
                  volume-data-buckram-height
                  volume-data-buckram-width))

(define backcard-row
  (data-row-maker (backcard-label)
                  volume-data-backcard-height
                  volume-data-backcard-width))

(define (table-body title color volumes)
  (string-append
   (header-row title color volumes)
   (subheader-row (length volumes))
   (cardboard-row volumes)
   (data-cline (length volumes))
   (paper-row volumes)
   (data-cline (length volumes))
   (buckram-row volumes)
   (data-cline (length volumes))
   (backcard-row volumes)))

(define (write-to-tex-file filename tickets)
  (call-with-output-file filename #:exists 'replace
    (lambda (out)
      (display
       (doc-setup
        (string-join
         (map (lambda (my-ticket)
                (if (eqv? my-ticket 'newpage)
                    (format "\n\\vfill\\newpage\n")
                    (table-setup
                     (column-args (length (ticket-volume-data-list my-ticket)))
                     (table-body (ticket-title my-ticket)
                                 (ticket-color my-ticket)
                                 (ticket-volume-data-list my-ticket)))))
              tickets)
         (format "\n\\vskip ~amm\n\n" (ticket-spacing))))
       out))))



